"""Identidade autenticada. A autorização é sempre server-side (FR-002)."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import User
from app.shared.errors import ApiError


class Role(StrEnum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: uuid.UUID
    subject: str
    roles: frozenset[Role]

    def has(self, role: Role) -> bool:
        return role in self.roles


_SUBJECT = re.compile(r"^[A-Za-z0-9._@-]{1,128}$")


def _ensure_user(db: Session, subject: str) -> uuid.UUID:
    stmt = (
        insert(User)
        .values(id=uuid.uuid4(), idp_subject=subject, display_name=None, created_at=datetime.now(UTC))
        .on_conflict_do_nothing(index_elements=[User.idp_subject])
    )
    db.execute(stmt)
    user_id = db.execute(select(User.id).where(User.idp_subject == subject)).scalar_one()
    db.commit()
    return user_id


def dev_principal(request: Request) -> Principal:
    """Autenticação de DESENVOLVIMENTO por cabeçalho (X-Dev-User, X-Dev-Roles).

    Só é instalada quando AUTH_MODE=dev e APP_ENV in {local,test} (ver Settings.check).
    Não representa autenticação real e não deve ser exposta fora do ambiente local.
    """
    subject = request.headers.get("x-dev-user", "")
    if not _SUBJECT.match(subject):
        raise ApiError(401, "UNAUTHENTICATED", "Autenticação ausente ou inválida.")
    raw_roles = request.headers.get("x-dev-roles", Role.STUDENT.value)
    try:
        roles = frozenset(Role(r.strip()) for r in raw_roles.split(",") if r.strip())
    except ValueError as exc:
        raise ApiError(401, "UNAUTHENTICATED", "Papel inválido.") from exc
    factory = request.app.state.session_factory
    with factory() as db:
        user_id = _ensure_user(db, subject)
    return Principal(user_id=user_id, subject=subject, roles=roles or frozenset({Role.STUDENT}))


def get_principal(request: Request) -> Principal:
    authenticator = request.app.state.authenticator
    principal: Principal = authenticator(request)
    return principal


def require_admin(principal: Principal = Depends(get_principal)) -> Principal:  # noqa: B008
    if not principal.has(Role.ADMIN):
        raise ApiError(403, "FORBIDDEN", "Operação restrita a administradores.")
    return principal
