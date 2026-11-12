"""Gestão de sessões: criação idempotente, consulta com ownership e encerramento (FR-020-026)."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.audit import service as audit
from app.db.models import LabRelease, LabSession, LabVariant
from app.identity.principal import Principal, Role
from app.jobs.queue import JobKind, enqueue
from app.sessions.state_machine import (
    ACTIVE,
    InvalidTransitionError,
    SessionEvent,
    SessionStatus,
    transition,
)
from app.shared.errors import ApiError, not_found
from app.shared.logging import correlation_id_var


@dataclass(frozen=True, slots=True)
class CreateSessionCommand:
    lab_id: str
    version: str
    variant_id: str

    def fingerprint(self) -> str:
        body = json.dumps(
            {"labId": self.lab_id, "version": self.version, "variantId": self.variant_id},
            sort_keys=True,
            separators=(",", ":"),
        )
        return "sha256:" + hashlib.sha256(body.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class CreateSessionResult:
    session: LabSession
    created: bool


def apply_event(
    db: Session,
    s: LabSession,
    event: SessionEvent,
    *,
    now: datetime,
    actor_id: str,
    error_code: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> SessionStatus:
    """Aplica transição validada + auditoria. A persistência usa optimistic locking (version_num)."""
    current = SessionStatus(s.status)
    new = transition(current, event)
    s.status = new.value
    s.updated_at = now
    if error_code is not None:
        s.last_error_code = error_code
    audit.record(
        db,
        now=now,
        actor_id=actor_id,
        action=f"session.{new.value.lower()}",
        resource_kind="lab_session",
        resource_id=str(s.id),
        metadata={"from": current.value, "trigger": event.value, **(metadata or {})},
        trace_id=s.correlation_id,
    )
    return new


def create_session(
    db: Session,
    *,
    principal: Principal,
    cmd: CreateSessionCommand,
    idempotency_key: str,
    now: datetime,
    max_attempts: int,
    provision_timeout: timedelta,
) -> CreateSessionResult:
    release = db.execute(
        select(LabRelease).where(
            LabRelease.lab_id == cmd.lab_id,
            LabRelease.version == cmd.version,
            LabRelease.status == "published",
        )
    ).scalar_one_or_none()
    if release is None:
        raise not_found("Laboratório")
    variant = db.execute(
        select(LabVariant).where(
            LabVariant.release_id == release.id, LabVariant.variant_key == cmd.variant_id
        )
    ).scalar_one_or_none()
    if variant is None:
        raise not_found("Variante")
    # TODO(IMP-204/205): verificar atribuição por turma e reservar quota antes de criar.

    fingerprint = cmd.fingerprint()
    session_id = uuid.uuid4()
    cid = correlation_id_var.get()
    inserted = db.execute(
        insert(LabSession)
        .values(
            id=session_id,
            user_id=principal.user_id,
            release_id=release.id,
            variant_id=variant.id,
            status=SessionStatus.REQUESTED.value,
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
            # TTL conta desde a solicitação e limita a vida total da sessão (premissa registrada em 25).
            expires_at=now + timedelta(minutes=variant.ttl_minutes),
            correlation_id=cid,
            created_at=now,
            updated_at=now,
            version_num=1,
        )
        .on_conflict_do_nothing()
        .returning(LabSession.id)
    ).scalar_one_or_none()

    if inserted is None:
        db.rollback()
        existing = db.execute(
            select(LabSession).where(
                LabSession.user_id == principal.user_id, LabSession.idempotency_key == idempotency_key
            )
        ).scalar_one_or_none()
        if existing is not None:
            if existing.request_fingerprint != fingerprint:
                raise ApiError(
                    409, "IDEMPOTENCY_KEY_REUSED", "Idempotency-Key já usada com outro corpo de requisição."
                )
            return CreateSessionResult(existing, created=False)
        active = db.execute(
            select(LabSession).where(
                LabSession.user_id == principal.user_id,
                LabSession.release_id == release.id,
                LabSession.status.in_([s.value for s in ACTIVE]),
            )
        ).scalar_one_or_none()
        raise ApiError(
            409,
            "SESSION_ALREADY_ACTIVE",
            "Já existe uma sessão ativa para este laboratório.",
            {"sessionId": str(active.id)} if active else {},
        )

    enqueue(
        db,
        kind=JobKind.PROVISION,
        session_id=session_id,
        now=now,
        max_attempts=max_attempts,
        deadline_at=now + provision_timeout,
        correlation_id=cid,
    )
    audit.record(
        db,
        now=now,
        actor_id=str(principal.user_id),
        action="session.requested",
        resource_kind="lab_session",
        resource_id=str(session_id),
        metadata={"lab_id": cmd.lab_id, "version": cmd.version, "variant_id": cmd.variant_id},
    )
    db.commit()
    created = db.get(LabSession, session_id)
    assert created is not None
    return CreateSessionResult(created, created=True)


def get_visible_session(db: Session, principal: Principal, session_id: uuid.UUID) -> LabSession:
    s = db.get(LabSession, session_id)
    # Não-donos recebem 404 (sem revelar existência). Admin enxerga para operação (FR-052).
    if s is None or (s.user_id != principal.user_id and not principal.has(Role.ADMIN)):
        raise not_found("Sessão")
    return s


def request_termination(
    db: Session, *, principal: Principal, session_id: uuid.UUID, now: datetime, max_attempts: int
) -> LabSession:
    s = get_visible_session(db, principal, session_id)
    db.refresh(s, with_for_update=True)
    status = SessionStatus(s.status)
    if status in (SessionStatus.TERMINATING, SessionStatus.TERMINATED):
        db.rollback()
        return s  # idempotente
    try:
        apply_event(
            db,
            s,
            SessionEvent.REQUEST_TERMINATION,
            now=now,
            actor_id=str(principal.user_id),
            metadata={"by_admin": s.user_id != principal.user_id},
        )
    except InvalidTransitionError as exc:  # pragma: no cover - todos os não terminais aceitam
        raise ApiError(409, "CONFLICT", str(exc)) from exc
    enqueue(
        db,
        kind=JobKind.TERMINATE,
        session_id=s.id,
        now=now,
        max_attempts=max_attempts,
        correlation_id=correlation_id_var.get() or s.correlation_id,
    )
    db.commit()
    return s


def session_view(db: Session, s: LabSession) -> dict[str, Any]:
    release = db.get(LabRelease, s.release_id)
    variant = db.get(LabVariant, s.variant_id)
    assert release is not None and variant is not None
    return {
        "sessionId": str(s.id),
        "status": s.status,
        "labId": release.lab_id,
        "version": release.version,
        "variantId": variant.variant_key,
        "expiresAt": s.expires_at.isoformat(),
        "createdAt": s.created_at.isoformat(),
        "updatedAt": s.updated_at.isoformat(),
        "lastErrorCode": s.last_error_code,
        "statusUrl": f"/api/v1/sessions/{s.id}",
    }


GATEWAY_STATUSES = frozenset({SessionStatus.READY, SessionStatus.ACTIVE})
TICKET_TTL_SECONDS = 60


def issue_gateway_ticket(
    db: Session, *, principal: Principal, session_id: uuid.UUID, purpose: str, secret: str, now: datetime
) -> tuple[str, LabSession]:
    """Ticket curto e de uso único para o gateway (docs/13 §2). Só o DONO recebe (nem admin)."""
    from app.gateway.tickets import Audience, Purpose, issue

    s = db.get(LabSession, session_id)
    if s is None or s.user_id != principal.user_id:
        raise not_found("Sessão")
    db.refresh(s, with_for_update=True)
    status = SessionStatus(s.status)
    if status not in GATEWAY_STATUSES or s.expires_at <= now:
        db.rollback()
        raise ApiError(409, "SESSION_NOT_READY", "Sessão não está pronta para conexão.", {"status": s.status})
    if status is SessionStatus.READY:
        apply_event(db, s, SessionEvent.FIRST_CONNECTION, now=now, actor_id=str(principal.user_id))
    pur = Purpose(purpose)
    token, claims = issue(
        secret,
        sid=str(s.id),
        sub=str(principal.user_id),
        purpose=pur,
        aud=Audience.TICKET,
        now=now,
        ttl_seconds=TICKET_TTL_SECONDS,
    )
    # Auditoria sem o token (docs/13 §2: tokens não devem ser logados).
    audit.record(
        db,
        now=now,
        actor_id=str(principal.user_id),
        action="session.gateway_ticket_issued",
        resource_kind="lab_session",
        resource_id=str(s.id),
        metadata={"purpose": pur.value, "jti": claims.jti},
    )
    db.commit()
    return token, s


def list_own_sessions(db: Session, principal: Principal) -> list[LabSession]:
    rows = db.execute(
        select(LabSession)
        .where(LabSession.user_id == principal.user_id, LabSession.status.in_([x.value for x in ACTIVE]))
        .order_by(LabSession.created_at.desc())
    ).scalars()
    return list(rows)


def steps_view(db: Session, s: LabSession) -> list[dict[str, Any]]:
    """Etapas da sessão (docs/13 §3, docs/21). Desbloqueio é decidido aqui, nunca pelo frontend.

    Enquanto a validação (IMP-401) não existe, apenas a primeira etapa fica disponível; etapas
    bloqueadas expõem só metadados (sem instruções, dicas ou referências de validador).
    """
    release = db.get(LabRelease, s.release_id)
    assert release is not None
    out: list[dict[str, Any]] = []
    for step in sorted(release.manifest["steps"], key=lambda x: x["order"]):
        unlocked = step["order"] == 1
        item: dict[str, Any] = {
            "id": step["id"],
            "order": step["order"],
            "title": step["title"],
            "points": step["points"],
            "status": "AVAILABLE" if unlocked else "LOCKED",
        }
        if unlocked:
            item.update(
                explanation=step["explanation"],
                task=step["task"],
                concept=step["concept"],
                hintsAvailable=len(step.get("hints", [])),
            )
        out.append(item)
    return out
