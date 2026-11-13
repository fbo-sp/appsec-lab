"""Resolução server-side ``session_id → destino interno`` para o gateway (nunca vinda do navegador)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import LabSession, LabVariant, RuntimeInstance


@dataclass(frozen=True, slots=True)
class SessionTarget:
    session_id: str
    user_id: str
    status: str
    expires_at: datetime
    host: str | None
    port: int | None
    # Prazo máximo alcançável com as renovações restantes (ADR-009/011): limita a vida do grant, que
    # assim sobrevive a uma renovação; o prazo efetivo (``expires_at``) é revalidado a cada requisição.
    max_expires_at: datetime | None = None


class SessionResolver(Protocol):
    def resolve(self, session_id: str) -> SessionTarget | None: ...


class SqlSessionResolver:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._factory = session_factory

    def resolve(self, session_id: str) -> SessionTarget | None:
        try:
            sid = uuid.UUID(session_id)
        except ValueError:
            return None
        with self._factory() as db:
            row = db.execute(
                select(LabSession, RuntimeInstance, LabVariant)
                .outerjoin(RuntimeInstance, RuntimeInstance.session_id == LabSession.id)
                .outerjoin(LabVariant, LabVariant.id == LabSession.variant_id)
                .where(LabSession.id == sid)
            ).first()
        if row is None:
            return None
        s, inst, variant = row
        max_exp = s.expires_at
        if variant is not None:
            remaining = max(0, variant.max_renewals - s.renewals)
            max_exp = s.expires_at + timedelta(minutes=variant.ttl_minutes * remaining)
        return SessionTarget(
            str(s.id),
            str(s.user_id),
            s.status,
            s.expires_at,
            inst.endpoint_host if inst else None,
            inst.endpoint_port if inst else None,
            max_exp,
        )
