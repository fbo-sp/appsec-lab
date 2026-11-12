"""Resolução server-side ``session_id → destino interno`` para o gateway (nunca vinda do navegador)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import LabSession, RuntimeInstance


@dataclass(frozen=True, slots=True)
class SessionTarget:
    session_id: str
    user_id: str
    status: str
    expires_at: datetime
    host: str | None
    port: int | None


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
                select(LabSession, RuntimeInstance)
                .outerjoin(RuntimeInstance, RuntimeInstance.session_id == LabSession.id)
                .where(LabSession.id == sid)
            ).first()
        if row is None:
            return None
        s, inst = row
        return SessionTarget(
            str(s.id),
            str(s.user_id),
            s.status,
            s.expires_at,
            inst.endpoint_host if inst else None,
            inst.endpoint_port if inst else None,
        )
