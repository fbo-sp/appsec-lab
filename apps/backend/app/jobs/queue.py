"""Fila de jobs no PostgreSQL (ADR-007): enfileiramento transacional, claim com
``FOR UPDATE SKIP LOCKED`` e lease, retry com backoff exponencial limitado.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from sqlalchemy import or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Job


class JobKind(StrEnum):
    PROVISION = "PROVISION"
    TERMINATE = "TERMINATE"
    EVALUATE = "EVALUATE"


@dataclass(frozen=True, slots=True)
class ClaimedJob:
    id: uuid.UUID
    kind: JobKind
    session_id: uuid.UUID
    attempts: int
    max_attempts: int
    deadline_at: datetime | None
    correlation_id: str | None


def enqueue(
    db: Session,
    *,
    kind: JobKind,
    session_id: uuid.UUID,
    now: datetime,
    max_attempts: int,
    deadline_at: datetime | None = None,
    correlation_id: str | None = None,
) -> bool:
    """Enfileira se não houver job pendente do mesmo tipo para a sessão. Retorna True se criou."""
    stmt = (
        insert(Job)
        .values(
            id=uuid.uuid4(),
            kind=kind.value,
            session_id=session_id,
            status="queued",
            attempts=0,
            max_attempts=max_attempts,
            run_at=now,
            deadline_at=deadline_at,
            correlation_id=correlation_id,
            created_at=now,
            updated_at=now,
        )
        .on_conflict_do_nothing(
            index_elements=[Job.kind, Job.session_id],
            index_where=Job.status.in_(("queued", "running")),
        )
        .returning(Job.id)
    )
    return db.execute(stmt).scalar_one_or_none() is not None


def claim(db: Session, *, worker_id: str, now: datetime, lease: timedelta) -> ClaimedJob | None:
    """Captura um job disponível (ou com lease vencido) e confirma imediatamente o lease."""
    candidate = (
        select(Job.id)
        .where(
            or_(
                (Job.status == "queued") & (Job.run_at <= now),
                (Job.status == "running") & (Job.lease_expires_at < now),
            )
        )
        .order_by(Job.run_at)
        .limit(1)
        .with_for_update(skip_locked=True)
        .scalar_subquery()
    )
    row = db.execute(
        update(Job)
        .where(Job.id == candidate)
        .values(status="running", lease_owner=worker_id, lease_expires_at=now + lease, updated_at=now)
        .returning(
            Job.id,
            Job.kind,
            Job.session_id,
            Job.attempts,
            Job.max_attempts,
            Job.deadline_at,
            Job.correlation_id,
        )
    ).one_or_none()
    db.commit()
    if row is None:
        return None
    return ClaimedJob(
        row.id,
        JobKind(row.kind),
        row.session_id,
        row.attempts,
        row.max_attempts,
        row.deadline_at,
        row.correlation_id,
    )


def _owned(job_id: uuid.UUID, worker_id: str):  # type: ignore[no-untyped-def]
    return (Job.id == job_id) & (Job.lease_owner == worker_id) & (Job.status == "running")


def complete(db: Session, job_id: uuid.UUID, worker_id: str, now: datetime) -> None:
    db.execute(
        update(Job)
        .where(_owned(job_id, worker_id))
        .values(status="succeeded", lease_owner=None, lease_expires_at=None, updated_at=now)
    )


def reschedule(db: Session, job_id: uuid.UUID, worker_id: str, now: datetime, delay: timedelta) -> None:
    """Re-agenda sem contar falha (ex.: aguardando readiness)."""
    db.execute(
        update(Job)
        .where(_owned(job_id, worker_id))
        .values(status="queued", run_at=now + delay, lease_owner=None, lease_expires_at=None, updated_at=now)
    )


def fail(db: Session, job: ClaimedJob, worker_id: str, now: datetime, error: str) -> bool:
    """Registra falha. Retorna True se ainda há tentativas (re-agendado) ou False se esgotou (dead)."""
    attempts = job.attempts + 1
    if attempts >= job.max_attempts:
        db.execute(
            update(Job)
            .where(_owned(job.id, worker_id))
            .values(
                status="dead",
                attempts=attempts,
                last_error=error[:500],
                lease_owner=None,
                lease_expires_at=None,
                updated_at=now,
            )
        )
        return False
    backoff = timedelta(seconds=min(60, 2**attempts))
    db.execute(
        update(Job)
        .where(_owned(job.id, worker_id))
        .values(
            status="queued",
            attempts=attempts,
            last_error=error[:500],
            run_at=now + backoff,
            lease_owner=None,
            lease_expires_at=None,
            updated_at=now,
        )
    )
    return True
