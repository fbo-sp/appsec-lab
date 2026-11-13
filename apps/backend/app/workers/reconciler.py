"""Reconciliador (FR-025, NFR-007, TM-14): compara estado desejado no banco com o runtime real.

Ações idempotentes por passagem:
1. sessões vivas com ``expires_at`` vencido => EXPIRED + job TERMINATE;
1b. sessões prontas sem atividade há ``SESSION_IDLE_MINUTES`` => TERMINATING (motivo ``idle``) + TERMINATE
    (ADR-014: libera recursos; o progresso fica na tentativa);
2. sessões em EXPIRED/FAILED/COMPLETED/TERMINATING sem job TERMINATE pendente
   (ex.: job "dead") => re-enfileira TERMINATE;
3. runtimes de ``list_owned()`` sem sessão ou com sessão TERMINATED => terminate direto + auditoria.
Jobs com lease vencido são retomados pelo próprio ``claim``.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit import service as audit
from app.audit.service import SYSTEM_ACTOR
from app.db.models import Job, LabSession
from app.jobs import queue
from app.jobs.queue import JobKind
from app.runtime.port import RuntimeAdapterError
from app.sessions import service as sessions
from app.sessions.service import apply_event
from app.sessions.state_machine import EXPIRABLE, NEEDS_CLEANUP, SessionEvent, SessionStatus
from app.workers.provisioner import WorkerContext

_log = logging.getLogger("app.reconciler")


@dataclass
class ReconcileReport:
    expired: list[str] = field(default_factory=list)
    idle: list[str] = field(default_factory=list)
    requeued_terminations: list[str] = field(default_factory=list)
    orphans_removed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def reconcile_once(ctx: WorkerContext) -> ReconcileReport:
    report = ReconcileReport()
    now = ctx.clock.now()
    with ctx.session_factory() as db:
        expired = (
            db.execute(
                select(LabSession)
                .where(LabSession.expires_at <= now, LabSession.status.in_([s.value for s in EXPIRABLE]))
                .with_for_update(skip_locked=True)
            )
            .scalars()
            .all()
        )
        for s in expired:
            apply_event(
                db, s, SessionEvent.EXPIRE, now=now, actor_id=SYSTEM_ACTOR, metadata={"reason": "ttl_expired"}
            )
            queue.enqueue(
                db,
                kind=JobKind.TERMINATE,
                session_id=s.id,
                now=now,
                max_attempts=ctx.job_max_attempts,
                correlation_id=s.correlation_id,
            )
            report.expired.append(str(s.id))
        db.commit()

        if sessions.IDLE_MINUTES > 0:
            cutoff = now - timedelta(minutes=sessions.IDLE_MINUTES)
            idle = (
                db.execute(
                    select(LabSession)
                    .where(
                        LabSession.status.in_([st.value for st in sessions.GATEWAY_STATUSES]),
                        func.coalesce(LabSession.last_activity_at, LabSession.ready_at) <= cutoff,
                    )
                    .with_for_update(skip_locked=True)
                )
                .scalars()
                .all()
            )
            for s in idle:
                apply_event(
                    db,
                    s,
                    SessionEvent.REQUEST_TERMINATION,
                    now=now,
                    actor_id=SYSTEM_ACTOR,
                    metadata={"reason": "idle", "idle_minutes": sessions.IDLE_MINUTES},
                )
                s.end_reason = "idle"
                queue.enqueue(
                    db,
                    kind=JobKind.TERMINATE,
                    session_id=s.id,
                    now=now,
                    max_attempts=ctx.job_max_attempts,
                    correlation_id=s.correlation_id,
                )
                report.idle.append(str(s.id))
            db.commit()

        pending = select(Job.session_id).where(
            Job.kind == JobKind.TERMINATE.value, Job.status.in_(("queued", "running"))
        )
        needs_cleanup = [st.value for st in NEEDS_CLEANUP]
        stuck = (
            db.execute(
                select(LabSession.id).where(
                    LabSession.status.in_(needs_cleanup), LabSession.id.not_in(pending)
                )
            )
            .scalars()
            .all()
        )
        for sid in stuck:
            if queue.enqueue(
                db, kind=JobKind.TERMINATE, session_id=sid, now=now, max_attempts=ctx.job_max_attempts
            ):
                report.requeued_terminations.append(str(sid))
        db.commit()

    try:
        owned = ctx.runtime.list_owned()
    except RuntimeAdapterError as exc:
        report.errors.append(f"list_owned: {exc}")
        return report
    for rt in owned:
        with ctx.session_factory() as db:
            owner = _session_or_none(db, rt.session_id)
            if owner is not None and SessionStatus(owner.status) is not SessionStatus.TERMINATED:
                continue
            try:
                ctx.runtime.terminate(rt.runtime_ref)
            except RuntimeAdapterError as exc:
                report.errors.append(f"terminate {rt.runtime_ref}: {exc}")
                continue
            audit.record(
                db,
                now=now,
                actor_id=SYSTEM_ACTOR,
                action="runtime.orphan_removed",
                resource_kind="runtime_instance",
                resource_id=rt.runtime_ref,
                metadata={"session_id": rt.session_id, "session_known": owner is not None},
            )
            db.commit()
            report.orphans_removed.append(rt.runtime_ref)
    if report.expired or report.orphans_removed or report.requeued_terminations or report.errors:
        _log.info(
            "reconcile_pass",
            extra={
                "event": "reconciler.pass",
                "expired": len(report.expired),
                "orphans_removed": len(report.orphans_removed),
                "requeued": len(report.requeued_terminations),
                "errors": report.errors,
            },
        )
    return report


def _session_or_none(db: Session, raw_id: str) -> LabSession | None:
    try:
        sid = uuid.UUID(raw_id)
    except ValueError:
        return None
    return db.get(LabSession, sid)
