"""Worker de ciclo de vida: executa jobs PROVISION e TERMINATE contra o RuntimePort.

Regras (docs/08 §5-6, docs/09 §5):
- a transição é persistida ANTES do efeito externo;
- o adapter é chamado com ``session_id`` como chave idempotente;
- falha transitória => retry com backoff; esgotou => FAILED + job de limpeza;
- TERMINATED só após confirmar ausência do runtime (``inspect`` == ABSENT).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.audit.service import SYSTEM_ACTOR
from app.db.models import LabRelease, LabSession, LabVariant, RuntimeInstance, StepSubmission
from app.jobs import queue
from app.jobs.queue import ClaimedJob, JobKind
from app.progress.service import finalize
from app.runtime.port import (
    ProvisionRequest,
    ResourceLimits,
    RuntimePermanentError,
    RuntimePhase,
    RuntimePort,
    RuntimeTransientError,
)
from app.sessions.service import apply_event
from app.sessions.state_machine import SessionEvent, SessionStatus
from app.shared.clock import Clock
from app.shared.logging import correlation_id_var
from app.validation.port import EvaluationOutcome, EvaluationRequest, EvaluatorPort
from app.validation.suites import HttpSuite, get_suite

_log = logging.getLogger("app.worker")
READINESS_POLL = timedelta(seconds=1)


@dataclass
class WorkerContext:
    session_factory: sessionmaker[Session]
    runtime: RuntimePort
    clock: Clock
    worker_id: str
    lease: timedelta
    job_max_attempts: int
    evaluator: EvaluatorPort | None = None


def build_request(db: Session, s: LabSession) -> ProvisionRequest:
    """Resolve a requisição a partir da release aprovada — nunca de entrada do cliente."""
    release = db.get(LabRelease, s.release_id)
    variant = db.get(LabVariant, s.variant_id)
    assert release is not None and variant is not None
    spec = next(v for v in release.manifest["variants"] if v["id"] == variant.variant_key)
    res = spec["resources"]
    return ProvisionRequest(
        session_id=str(s.id),
        lab_release=f"{release.lab_id}@{release.version}",
        variant_id=variant.variant_key,
        image_digest=variant.image_digest,
        runtime_profile=variant.runtime_profile,
        resources=ResourceLimits(
            res["cpuMillicores"], res["memoryMiB"], res["storageMiB"], res.get("pidsMax", 64)
        ),
        egress_profile=spec.get("network", {}).get("egressProfile", "deny-all"),
        exposed_port=spec["startup"]["port"],
        expires_at=s.expires_at,
        startup_command=tuple(spec["startup"]["command"]),
        workspace_path=spec["workspacePath"],
    )


def run_once(ctx: WorkerContext) -> bool:
    """Processa no máximo um job. Retorna True se algum job foi capturado."""
    with ctx.session_factory() as db:
        job = queue.claim(db, worker_id=ctx.worker_id, now=ctx.clock.now(), lease=ctx.lease)
    if job is None:
        return False
    token = correlation_id_var.set(job.correlation_id)
    try:
        _log.info(
            "job_claimed",
            extra={
                "event": "job.claimed",
                "job_id": str(job.id),
                "kind": job.kind.value,
                "session_id": str(job.session_id),
                "attempts": job.attempts,
            },
        )
        if job.kind is JobKind.PROVISION:
            _provision(ctx, job)
        elif job.kind is JobKind.EVALUATE:
            _evaluate(ctx, job)
        else:
            _terminate(ctx, job)
    finally:
        correlation_id_var.reset(token)
    return True


def _lock_session(db: Session, session_id: uuid.UUID) -> LabSession:
    s = db.execute(select(LabSession).where(LabSession.id == session_id).with_for_update()).scalar_one()
    return s


def _fail_session(ctx: WorkerContext, db: Session, s: LabSession, code: str) -> None:
    now = ctx.clock.now()
    apply_event(db, s, SessionEvent.FAIL, now=now, actor_id=SYSTEM_ACTOR, error_code=code)
    # Fail closed + limpeza: qualquer recurso parcial é removido (docs/02 §9).
    queue.enqueue(
        db,
        kind=JobKind.TERMINATE,
        session_id=s.id,
        now=now,
        max_attempts=ctx.job_max_attempts,
        correlation_id=s.correlation_id,
    )


def _provision(ctx: WorkerContext, job: ClaimedJob) -> None:
    now = ctx.clock.now()
    with ctx.session_factory() as db:
        s = _lock_session(db, job.session_id)
        status = SessionStatus(s.status)
        if status not in (SessionStatus.REQUESTED, SessionStatus.PROVISIONING):
            # Sessão foi encerrada/expirada enquanto o job aguardava: nada a provisionar.
            queue.complete(db, job.id, ctx.worker_id, now)
            db.commit()
            return
        if job.deadline_at is not None and now >= job.deadline_at:
            _fail_session(ctx, db, s, "PROVISION_TIMEOUT")
            queue.complete(db, job.id, ctx.worker_id, now)
            db.commit()
            return
        if status is SessionStatus.REQUESTED:
            apply_event(db, s, SessionEvent.START_PROVISIONING, now=now, actor_id=SYSTEM_ACTOR)
        request = build_request(db, s)
        db.commit()  # persiste PROVISIONING antes do efeito externo

    try:
        ref = ctx.runtime.provision(request)
        phase = ctx.runtime.inspect(ref).phase
        endpoint = ctx.runtime.endpoint(ref) if phase is RuntimePhase.READY else None
    except RuntimeTransientError as exc:
        with ctx.session_factory() as db:
            retry = queue.fail(db, job, ctx.worker_id, ctx.clock.now(), str(exc))
            if not retry:
                s = _lock_session(db, job.session_id)
                if SessionStatus(s.status) is SessionStatus.PROVISIONING:
                    _fail_session(ctx, db, s, "RUNTIME_UNAVAILABLE")
            db.commit()
        _log.warning(
            "provision_transient_error",
            extra={
                "event": "session.provision_error",
                "session_id": str(job.session_id),
                "retry": retry,
                "error": str(exc),
            },
        )
        return
    except RuntimePermanentError as exc:
        with ctx.session_factory() as db:
            s = _lock_session(db, job.session_id)
            if SessionStatus(s.status) is SessionStatus.PROVISIONING:
                _fail_session(ctx, db, s, "PROVISION_REJECTED")
            queue.complete(db, job.id, ctx.worker_id, ctx.clock.now())
            db.commit()
        _log.error(
            "provision_permanent_error",
            extra={"event": "session.provision_error", "session_id": str(job.session_id), "error": str(exc)},
        )
        return

    now = ctx.clock.now()
    with ctx.session_factory() as db:
        s = _lock_session(db, job.session_id)
        inst = db.execute(
            select(RuntimeInstance).where(RuntimeInstance.session_id == s.id)
        ).scalar_one_or_none()
        if inst is None:
            inst = RuntimeInstance(
                id=uuid.uuid4(),
                session_id=s.id,
                provider=ctx.runtime.provider,
                external_ref=ref,
                status=phase.value,
                created_at=now,
            )
            db.add(inst)
        inst.status = phase.value
        if endpoint is not None:
            inst.endpoint_host, inst.endpoint_port = endpoint.host, endpoint.port
        if SessionStatus(s.status) is not SessionStatus.PROVISIONING:
            # Encerrada durante o provisionamento: o job TERMINATE (ou o reconciliador) remove o runtime.
            queue.complete(db, job.id, ctx.worker_id, now)
        elif phase is RuntimePhase.READY:
            provision_ms = max(0, int((now - s.created_at).total_seconds() * 1000))
            s.ready_at, s.provision_ms = now, provision_ms
            apply_event(
                db,
                s,
                SessionEvent.RUNTIME_READY,
                now=now,
                actor_id=SYSTEM_ACTOR,
                metadata={"provider": ctx.runtime.provider, "provision_ms": provision_ms},
            )
            _log.info(
                "session_ready",
                extra={"event": "session.ready", "session_id": str(s.id), "provision_ms": provision_ms},
            )
            queue.complete(db, job.id, ctx.worker_id, now)
        elif phase is RuntimePhase.FAILED:
            _fail_session(ctx, db, s, "RUNTIME_FAILED")
            queue.complete(db, job.id, ctx.worker_id, now)
        else:
            queue.reschedule(db, job.id, ctx.worker_id, now, READINESS_POLL)
        db.commit()


def _terminate(ctx: WorkerContext, job: ClaimedJob) -> None:
    now = ctx.clock.now()
    with ctx.session_factory() as db:
        s = _lock_session(db, job.session_id)
        status = SessionStatus(s.status)
        if status is SessionStatus.TERMINATED:
            queue.complete(db, job.id, ctx.worker_id, now)
            db.commit()
            return
        if status is not SessionStatus.TERMINATING:
            apply_event(db, s, SessionEvent.REQUEST_TERMINATION, now=now, actor_id=SYSTEM_ACTOR)
        db.commit()
    ref = ctx.runtime.ref_for(str(job.session_id))
    try:
        ctx.runtime.terminate(ref)
        phase = ctx.runtime.inspect(ref).phase
    except (RuntimeTransientError, RuntimePermanentError) as exc:
        with ctx.session_factory() as db:
            retry = queue.fail(db, job, ctx.worker_id, ctx.clock.now(), str(exc))
            db.commit()
        # Job "dead" mantém a sessão em TERMINATING; o reconciliador re-enfileira e alerta (TM-14).
        _log.warning(
            "terminate_error",
            extra={
                "event": "session.terminate_error",
                "session_id": str(job.session_id),
                "retry": retry,
                "error": str(exc),
            },
        )
        return
    now = ctx.clock.now()
    with ctx.session_factory() as db:
        s = _lock_session(db, job.session_id)
        if phase is RuntimePhase.ABSENT:
            inst = db.execute(
                select(RuntimeInstance).where(RuntimeInstance.session_id == s.id)
            ).scalar_one_or_none()
            if inst is not None:
                inst.status = RuntimePhase.ABSENT.value
                inst.terminated_at = now
            apply_event(db, s, SessionEvent.RUNTIME_GONE, now=now, actor_id=SYSTEM_ACTOR)
            queue.complete(db, job.id, ctx.worker_id, now)
        else:
            queue.reschedule(db, job.id, ctx.worker_id, now, READINESS_POLL)
        db.commit()


TECH_ERROR_FEEDBACK = (
    "Não foi possível concluir a validação por uma falha técnica. "
    "Isso não conta contra você; tente novamente."
)


def _evaluate(ctx: WorkerContext, job: ClaimedJob) -> None:
    """Avaliação comportamental (ADR-010) fora do workspace. Falha técnica => ERROR, nunca aprovação."""
    now = ctx.clock.now()
    with ctx.session_factory() as db:
        sub = db.execute(
            select(StepSubmission)
            .where(
                StepSubmission.session_id == job.session_id, StepSubmission.status.in_(("QUEUED", "RUNNING"))
            )
            .with_for_update()
        ).scalar_one_or_none()
        if sub is None:
            queue.complete(db, job.id, ctx.worker_id, now)
            db.commit()
            return
        s = db.get(LabSession, job.session_id)
        assert s is not None
        suite = get_suite(sub.validator_ref)
        ref = ctx.runtime.ref_for(str(s.id))
        if SessionStatus(s.status) not in (SessionStatus.READY, SessionStatus.ACTIVE) or not isinstance(
            suite, HttpSuite
        ):
            finalize(
                db,
                sub,
                passed=None,
                criteria=[],
                feedback=TECH_ERROR_FEEDBACK,
                now=now,
                error_code="SESSION_NOT_READY",
            )
            queue.complete(db, job.id, ctx.worker_id, now)
            db.commit()
            return
        base = build_request(db, s)
        sub.status, sub.started_at = "RUNNING", now
        request = EvaluationRequest(
            submission_id=str(sub.id),
            runtime_ref=ref,
            image_digest=base.image_digest,
            workspace_path=base.workspace_path,
            startup_command=base.startup_command,
            app_port=base.exposed_port,
            checks=[
                {
                    "id": c.id,
                    "path": c.path,
                    "method": c.method,
                    "form": c.form,
                    "expect_status": c.expect_status,
                    "contains": list(c.contains),
                    "not_contains": list(c.not_contains),
                }
                for c in suite.checks
            ],
            cpu_millicores=base.resources.cpu_millicores,
            memory_mib=base.resources.memory_mib,
            pids_max=base.resources.pids_max,
            timeout_seconds=suite.timeout_seconds,
        )
        sub_id = sub.id
        db.commit()  # RUNNING persistido antes do efeito externo

    outcome: EvaluationOutcome | None = None
    if ctx.evaluator is not None:
        try:
            outcome = ctx.evaluator.evaluate(request)
        except Exception as exc:  # falha técnica nunca aprova nem reprova (fail closed => ERROR)
            outcome = EvaluationOutcome(None, {}, f"{type(exc).__name__}")
    now = ctx.clock.now()
    with ctx.session_factory() as db:
        sub = db.execute(
            select(StepSubmission).where(StepSubmission.id == sub_id).with_for_update()
        ).scalar_one()
        if sub.status != "RUNNING":
            queue.complete(db, job.id, ctx.worker_id, now)
            db.commit()
            return
        if outcome is None or outcome.error:
            sub.snapshot_digest = outcome.snapshot_digest if outcome else None
            finalize(
                db,
                sub,
                passed=None,
                criteria=[],
                feedback=TECH_ERROR_FEEDBACK,
                now=now,
                error_code="EVALUATION_ERROR",
            )
            _log.warning(
                "evaluation_error",
                extra={
                    "event": "evaluation.error",
                    "submission_id": str(sub_id),
                    "error": outcome.error if outcome else "sem avaliador",
                },
            )
        else:
            criteria = [
                {"id": c.id, "description": c.description, "passed": bool(outcome.results.get(c.id, False))}
                for c in suite.checks
            ]
            passed = all(c["passed"] for c in criteria)
            sub.snapshot_digest = outcome.snapshot_digest
            finalize(
                db,
                sub,
                passed=passed,
                criteria=criteria,
                feedback=suite.success_feedback if passed else suite.failure_feedback,
                now=now,
            )
        queue.complete(db, job.id, ctx.worker_id, now)
        db.commit()
