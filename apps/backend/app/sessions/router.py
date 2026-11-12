from __future__ import annotations

import re
import uuid
from datetime import timedelta
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Header, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.config import Settings
from app.deps import get_clock, get_db, get_settings
from app.identity.principal import Principal, get_principal
from app.sessions import service
from app.shared.clock import Clock
from app.shared.errors import ApiError

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])
_KEY = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")


class CreateSessionBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lab_id: str = Field(alias="labId", pattern=r"^LAB-[0-9]{3}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$", max_length=32)
    variant_id: str = Field(alias="variantId", pattern=r"^[a-z][a-z0-9-]{0,62}$")


def _key(value: str | None) -> str:
    if value is None or not _KEY.match(value):
        raise ApiError(
            400, "VALIDATION_ERROR", "Cabeçalho Idempotency-Key ausente ou inválido (8-128 caracteres)."
        )
    return value


@router.post("", status_code=202)
def create_session(
    body: CreateSessionBody,
    response: Response,
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
    clock: Annotated[Clock, Depends(get_clock)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, Any]:
    result = service.create_session(
        db,
        principal=principal,
        cmd=service.CreateSessionCommand(body.lab_id, body.version, body.variant_id),
        idempotency_key=_key(idempotency_key),
        now=clock.now(),
        max_attempts=settings.job_max_attempts,
        provision_timeout=timedelta(seconds=settings.provision_timeout_seconds),
    )
    response.headers["Location"] = f"/api/v1/sessions/{result.session.id}"
    if not result.created:
        response.headers["Idempotent-Replayed"] = "true"
    return service.session_view(db, result.session)


class TicketBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    purpose: Literal["workspace", "preview"]


@router.get("")
def list_sessions(
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    """Sessões não terminais do próprio usuário (retomada pela interface)."""
    return {"items": [service.session_view(db, s) for s in service.list_own_sessions(db, principal)]}


@router.post("/{session_id}/gateway-ticket")
def gateway_ticket(
    session_id: uuid.UUID,
    body: TicketBody,
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
    clock: Annotated[Clock, Depends(get_clock)],
    settings: Annotated[Settings, Depends(get_settings)],
    response: Response,
) -> dict[str, Any]:
    if settings.gateway_ticket_secret is None:
        raise ApiError(503, "GATEWAY_UNAVAILABLE", "Gateway de workspace não configurado neste ambiente.")
    token, s = service.issue_gateway_ticket(
        db,
        principal=principal,
        session_id=session_id,
        purpose=body.purpose,
        secret=settings.gateway_ticket_secret,
        now=clock.now(),
    )
    response.headers["Cache-Control"] = "no-store"
    if body.purpose == "workspace":
        url = f"{settings.gateway_workspace_url}/s/{s.id}/__cecyber/auth?ticket={token}"
    else:
        url = f"{settings.gateway_preview_url}/__cecyber/auth?ticket={token}"
    return {"url": url, "expiresInSeconds": service.TICKET_TTL_SECONDS, "status": s.status}


@router.get("/{session_id}")
def get_session(
    session_id: uuid.UUID,
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    return service.session_view(db, service.get_visible_session(db, principal, session_id))


@router.get("/{session_id}/steps")
def get_steps(
    session_id: uuid.UUID,
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    s = service.get_visible_session(db, principal, session_id)
    return {"sessionId": str(s.id), "items": service.steps_view(db, s)}


@router.delete("/{session_id}", status_code=202)
def terminate_session(
    session_id: uuid.UUID,
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
    clock: Annotated[Clock, Depends(get_clock)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    s = service.request_termination(
        db,
        principal=principal,
        session_id=session_id,
        now=clock.now(),
        max_attempts=settings.job_max_attempts,
    )
    return service.session_view(db, s)
