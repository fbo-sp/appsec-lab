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
from app.db.models import LabRelease, LabSession, LabVariant, RuntimeInstance
from app.jobs import queue
from app.jobs.queue import ClaimedJob, JobKind
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
        if (
            db.execute(select(RuntimeInstance).where(RuntimeInstance.session_id == s.id)).scalar_one_or_none()
            is None
        ):
            db.add(
                RuntimeInstance(
                    id=uuid.uuid4(),
                    session_id=s.id,
                    provider=ctx.runtime.provider,
                    external_ref=ref,
                    status=phase.value,
                    created_at=now,
                )
            )
        if SessionStatus(s.status) is not SessionStatus.PROVISIONING:
            # Encerrada durante o provisionamento: o job TERMINATE (ou o reconciliador) remove o runtime.
            queue.complete(db, job.id, ctx.worker_id, now)
        elif phase is RuntimePhase.READY:
            apply_event(
                db,
                s,
                SessionEvent.RUNTIME_READY,
                now=now,
                actor_id=SYSTEM_ACTOR,
                metadata={"provider": ctx.runtime.provider},
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
