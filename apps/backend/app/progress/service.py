"""Progresso acadêmico (ADR-005, IMP-401/404/405): tentativa, etapas, submissões e dicas.

Regras:
- o progresso pertence à tentativa (``lab_attempts``), não à sessão: sobrevive a expiração/encerramento;
- desbloqueio sequencial decidido no servidor; etapa ``LOCKED`` não aceita avaliação nem dicas;
- uma avaliação pendente por sessão; idempotência por ``Idempotency-Key``;
- aprovação da etapa, pontos, desbloqueio da próxima e conclusão da tentativa na MESMA transação;
- OPEN-04 (PO, 2026-11-12): dicas não descontam pontos e tentativas são ilimitadas (tudo registrado);
- falha técnica (``ERROR``) não reprova nem desbloqueia.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.audit import service as audit
from app.db.models import (
    HintUsage,
    LabAttempt,
    LabRelease,
    LabSession,
    LabStep,
    StepHint,
    StepProgress,
    StepSubmission,
)
from app.identity.principal import Principal
from app.jobs.queue import JobKind, enqueue
from app.sessions.state_machine import SessionStatus
from app.shared.errors import ApiError, not_found
from app.shared.logging import correlation_id_var
from app.validation.suites import AnswerSuite, get_suite, normalize_answer, suite_digest

LIVE = frozenset({SessionStatus.READY.value, SessionStatus.ACTIVE.value})
PENDING = ("QUEUED", "RUNNING")


def _steps(db: Session, release_id: uuid.UUID) -> list[LabStep]:
    return list(
        db.execute(
            select(LabStep).where(LabStep.release_id == release_id).order_by(LabStep.position)
        ).scalars()
    )


def ensure_attempt(db: Session, s: LabSession, now: datetime) -> LabAttempt:
    """Liga a sessão à tentativa aberta do aluno (ou cria uma, com o progresso inicial)."""
    if s.attempt_id is not None:
        att = db.get(LabAttempt, s.attempt_id)
        assert att is not None
        return att
    release = db.get(LabRelease, s.release_id)
    assert release is not None
    new_id = uuid.uuid4()
    created = db.execute(
        insert(LabAttempt)
        .values(
            id=new_id,
            user_id=s.user_id,
            release_id=s.release_id,
            variant_id=s.variant_id,
            status="IN_PROGRESS",
            score=0,
            started_at=now,
        )
        .on_conflict_do_nothing()
        .returning(LabAttempt.id)
    ).scalar_one_or_none()
    if created is not None:
        sequential = bool(release.manifest.get("policy", {}).get("sequentialUnlock", True))
        for i, step in enumerate(_steps(db, s.release_id)):
            db.add(
                StepProgress(
                    id=uuid.uuid4(),
                    attempt_id=new_id,
                    step_id=step.id,
                    status="AVAILABLE" if (i == 0 or not sequential) else "LOCKED",
                    points_awarded=0,
                    submissions=0,
                    updated_at=now,
                )
            )
        att_id = new_id
    else:
        att_id = db.execute(
            select(LabAttempt.id).where(
                LabAttempt.user_id == s.user_id,
                LabAttempt.release_id == s.release_id,
                LabAttempt.variant_id == s.variant_id,
                LabAttempt.status == "IN_PROGRESS",
            )
        ).scalar_one()
    s.attempt_id = att_id
    db.flush()
    att = db.get(LabAttempt, att_id)
    assert att is not None
    return att


def _owned_live_session(db: Session, principal: Principal, session_id: uuid.UUID) -> LabSession:
    s = db.get(LabSession, session_id)
    if s is None or s.user_id != principal.user_id:
        raise not_found("Sessão")
    return s


def _step_and_progress(
    db: Session, att: LabAttempt, release_id: uuid.UUID, step_key: str
) -> tuple[LabStep, StepProgress]:
    step = db.execute(
        select(LabStep).where(LabStep.release_id == release_id, LabStep.step_key == step_key)
    ).scalar_one_or_none()
    if step is None:
        raise not_found("Etapa")
    prog = db.execute(
        select(StepProgress)
        .where(StepProgress.attempt_id == att.id, StepProgress.step_id == step.id)
        .with_for_update()
    ).scalar_one()
    return step, prog


def _manifest_step(release: LabRelease, step_key: str) -> dict[str, Any]:
    return next(x for x in release.manifest["steps"] if x["id"] == step_key)


# -- leitura -----------------------------------------------------------------------------------------
def progress_view(db: Session, s: LabSession, now: datetime) -> dict[str, Any]:
    att = ensure_attempt(db, s, now)
    db.commit()
    release = db.get(LabRelease, s.release_id)
    assert release is not None
    rows = {
        p.step_id: p
        for p in db.execute(select(StepProgress).where(StepProgress.attempt_id == att.id)).scalars()
    }
    revealed: dict[uuid.UUID, list[int]] = {}
    for h in db.execute(select(HintUsage).where(HintUsage.attempt_id == att.id)).scalars():
        revealed.setdefault(h.step_id, []).append(h.level)
    items: list[dict[str, Any]] = []
    for step in _steps(db, s.release_id):
        prog = rows[step.id]
        m = _manifest_step(release, step.step_key)
        item: dict[str, Any] = {
            "id": step.step_key,
            "order": step.position,
            "title": step.title,
            "points": step.max_points,
            "status": prog.status,
            "pointsAwarded": prog.points_awarded,
            "submissions": prog.submissions,
        }
        if prog.status != "LOCKED":
            suite = get_suite(step.validator_ref)
            hints = sorted(
                db.execute(select(StepHint).where(StepHint.step_id == step.id)).scalars(),
                key=lambda h: h.level,
            )
            levels = sorted(revealed.get(step.id, []))
            item.update(
                explanation=m["explanation"],
                task=m["task"],
                concept=m["concept"],
                validation={
                    "type": suite.kind if suite else "unavailable",
                    "answerPrompt": suite.prompt if isinstance(suite, AnswerSuite) else None,
                },
                hints={
                    "available": len(hints),
                    "revealed": [{"level": h.level, "text": h.content} for h in hints if h.level in levels],
                },
                lastSubmission=_last_submission(db, att.id, step.id),
            )
        items.append(item)
    return {
        "sessionId": str(s.id),
        "attempt": {
            "id": str(att.id),
            "status": att.status,
            "score": att.score,
            "maxScore": sum(st.max_points for st in _steps(db, s.release_id)),
            "passingScore": release.manifest.get("policy", {}).get("finalPassingScore", 100),
            "startedAt": att.started_at.isoformat(),
            "completedAt": att.completed_at.isoformat() if att.completed_at else None,
            "hintsUsed": sum(len(v) for v in revealed.values()),
            "submissions": sum(p.submissions for p in rows.values()),
        },
        "items": items,
    }


def _last_submission(db: Session, attempt_id: uuid.UUID, step_id: uuid.UUID) -> dict[str, Any] | None:
    sub = db.execute(
        select(StepSubmission)
        .where(StepSubmission.attempt_id == attempt_id, StepSubmission.step_id == step_id)
        .order_by(StepSubmission.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    return submission_view(sub) if sub else None


def submission_view(sub: StepSubmission) -> dict[str, Any]:
    return {
        "evaluationId": str(sub.id),
        "status": sub.status,
        "criteria": sub.criteria,
        "feedback": sub.feedback,
        "createdAt": sub.created_at.isoformat(),
        "finishedAt": sub.finished_at.isoformat() if sub.finished_at else None,
    }


def get_submission(
    db: Session, principal: Principal, session_id: uuid.UUID, evaluation_id: uuid.UUID
) -> StepSubmission:
    s = _owned_live_session(db, principal, session_id)
    sub = db.get(StepSubmission, evaluation_id)
    if sub is None or sub.session_id != s.id:
        raise not_found("Avaliação")
    return sub


# -- submissão -----------------------------------------------------------------------------------------
def submit(
    db: Session,
    *,
    principal: Principal,
    session_id: uuid.UUID,
    step_key: str,
    answer: str | None,
    idempotency_key: str,
    now: datetime,
    max_attempts: int,
) -> tuple[StepSubmission, bool]:
    """Cria a submissão. ``answer`` é avaliado aqui; ``http`` vai para o worker. Retorna (sub, criada)."""
    s = _owned_live_session(db, principal, session_id)
    fingerprint = hashlib.sha256(json.dumps([step_key, answer], ensure_ascii=False).encode()).hexdigest()
    existing = db.execute(
        select(StepSubmission).where(
            StepSubmission.session_id == s.id, StepSubmission.idempotency_key == idempotency_key
        )
    ).scalar_one_or_none()
    if existing is not None:
        if existing.request_fingerprint != fingerprint:
            raise ApiError(409, "IDEMPOTENCY_KEY_REUSED", "Idempotency-Key já usada com outro conteúdo.")
        return existing, False
    db.refresh(s, with_for_update=True)
    if s.status not in LIVE or s.expires_at <= now:
        raise ApiError(409, "SESSION_NOT_READY", "A sessão não está ativa.", {"status": s.status})
    att = ensure_attempt(db, s, now)
    step, prog = _step_and_progress(db, att, s.release_id, step_key)
    if prog.status == "LOCKED":
        raise ApiError(409, "STEP_LOCKED", "Conclua a etapa anterior para liberar esta.")
    if prog.status == "PASSED":
        raise ApiError(409, "STEP_ALREADY_PASSED", "Esta etapa já foi concluída.")
    suite = get_suite(step.validator_ref)
    if suite is None:
        raise ApiError(503, "VALIDATOR_UNAVAILABLE", "Validador desta etapa não está disponível.")
    pending = db.execute(
        select(StepSubmission.id).where(StepSubmission.session_id == s.id, StepSubmission.status.in_(PENDING))
    ).first()
    if pending is not None:
        raise ApiError(409, "EVALUATION_IN_PROGRESS", "Já existe uma validação em andamento nesta sessão.")
    norm = normalize_answer(answer) if answer is not None else None
    if isinstance(suite, AnswerSuite) and not norm:
        raise ApiError(400, "VALIDATION_ERROR", "Informe a resposta da etapa.")
    sub = StepSubmission(
        id=uuid.uuid4(),
        attempt_id=att.id,
        session_id=s.id,
        step_id=step.id,
        idempotency_key=idempotency_key,
        request_fingerprint=fingerprint,
        validator_ref=step.validator_ref,
        suite_digest=suite_digest(suite),
        answer=norm if isinstance(suite, AnswerSuite) else None,
        status="QUEUED",
        criteria=[],
        created_at=now,
    )
    db.add(sub)
    prog.submissions += 1
    prog.updated_at = now
    audit.record(
        db,
        now=now,
        actor_id=str(principal.user_id),
        action="step.submitted",
        resource_kind="step_submission",
        resource_id=str(sub.id),
        metadata={"session_id": str(s.id), "step": step_key, "validator": step.validator_ref},
    )
    if isinstance(suite, AnswerSuite):
        ok = norm in {normalize_answer(a) for a in suite.accepted}
        criteria = [{"id": "answer", "description": suite.prompt, "passed": ok}]
        finalize(
            db,
            sub,
            passed=ok,
            criteria=criteria,
            feedback=suite.success_feedback if ok else suite.failure_feedback,
            now=now,
        )
    else:
        db.flush()
        enqueue(
            db,
            kind=JobKind.EVALUATE,
            session_id=s.id,
            now=now,
            max_attempts=max_attempts,
            correlation_id=correlation_id_var.get() or s.correlation_id,
        )
    db.commit()
    return sub, True


def finalize(
    db: Session,
    sub: StepSubmission,
    *,
    passed: bool | None,
    criteria: list[dict[str, Any]],
    feedback: str | None,
    now: datetime,
    error_code: str | None = None,
) -> None:
    """Registra o resultado. ``passed=None`` = ERROR técnico (não reprova nem desbloqueia)."""
    sub.status = "ERROR" if passed is None else ("PASSED" if passed else "FAILED")
    sub.criteria = criteria
    sub.feedback = feedback
    sub.error_code = error_code
    sub.finished_at = now
    if passed:
        att = db.get(LabAttempt, sub.attempt_id, with_for_update=True)
        assert att is not None
        step = db.get(LabStep, sub.step_id)
        assert step is not None
        prog = db.execute(
            select(StepProgress)
            .where(StepProgress.attempt_id == att.id, StepProgress.step_id == step.id)
            .with_for_update()
        ).scalar_one()
        if prog.status != "PASSED":
            prog.status = "PASSED"
            prog.points_awarded = step.max_points
            prog.passed_at = now
            prog.updated_at = now
            nxt = db.execute(
                select(StepProgress)
                .join(LabStep, LabStep.id == StepProgress.step_id)
                .where(StepProgress.attempt_id == att.id, StepProgress.status == "LOCKED")
                .order_by(LabStep.position)
                .limit(1)
                .with_for_update()
            ).scalar_one_or_none()
            if nxt is not None:
                nxt.status = "AVAILABLE"
                nxt.updated_at = now
            all_progress = list(
                db.execute(select(StepProgress).where(StepProgress.attempt_id == att.id)).scalars()
            )
            att.score = sum(p.points_awarded for p in all_progress)
            if all(p.status == "PASSED" for p in all_progress):
                att.status = "COMPLETED"
                att.completed_at = now
                audit.record(
                    db,
                    now=now,
                    actor_id=str(att.user_id),
                    action="attempt.completed",
                    resource_kind="lab_attempt",
                    resource_id=str(att.id),
                    metadata={"score": att.score},
                )
    audit.record(
        db,
        now=now,
        actor_id="system",
        action=f"step.{sub.status.lower()}",
        resource_kind="step_submission",
        resource_id=str(sub.id),
        metadata={"error_code": error_code} if error_code else {},
    )


# -- dicas -----------------------------------------------------------------------------------------------
def reveal_hint(
    db: Session, *, principal: Principal, session_id: uuid.UUID, step_key: str, level: int, now: datetime
) -> dict[str, Any]:
    s = _owned_live_session(db, principal, session_id)
    att = ensure_attempt(db, s, now)
    step, prog = _step_and_progress(db, att, s.release_id, step_key)
    if prog.status == "LOCKED":
        raise ApiError(409, "STEP_LOCKED", "Dicas ficam disponíveis quando a etapa é liberada.")
    hint = db.execute(
        select(StepHint).where(StepHint.step_id == step.id, StepHint.level == level)
    ).scalar_one_or_none()
    if hint is None:
        raise not_found("Dica")
    used = set(
        db.execute(
            select(HintUsage.level).where(HintUsage.attempt_id == att.id, HintUsage.step_id == step.id)
        ).scalars()
    )
    if level > 1 and (level - 1) not in used:
        raise ApiError(409, "HINT_ORDER", "Revele as dicas em ordem.")
    if level not in used:
        db.add(HintUsage(id=uuid.uuid4(), attempt_id=att.id, step_id=step.id, level=level, revealed_at=now))
        audit.record(
            db,
            now=now,
            actor_id=str(principal.user_id),
            action="hint.revealed",
            resource_kind="lab_attempt",
            resource_id=str(att.id),
            metadata={"step": step_key, "level": level},
        )
    db.commit()
    return {"level": level, "text": hint.content, "penalty": 0}
