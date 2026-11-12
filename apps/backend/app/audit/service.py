"""Registro de eventos de auditoria na MESMA transação da ação auditada (NFR-010, BR-008)."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditEvent
from app.shared.logging import correlation_id_var

_log = logging.getLogger("app.audit")
SYSTEM_ACTOR = "system"


def record(
    db: Session,
    *,
    now: datetime,
    actor_id: str,
    action: str,
    resource_kind: str,
    resource_id: str,
    metadata: dict[str, Any] | None = None,
    trace_id: str | None = None,
) -> None:
    trace = trace_id or correlation_id_var.get()
    db.add(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            resource_kind=resource_kind,
            resource_id=resource_id,
            occurred_at=now,
            trace_id=trace,
            event_metadata=metadata or {},
        )
    )
    _log.info(
        action,
        extra={
            "event": action,
            "actor_id": actor_id,
            "resource_kind": resource_kind,
            "resource_id": resource_id,
            "trace_id": trace,
            **(metadata or {}),
        },
    )
