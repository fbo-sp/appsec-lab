"""Preferências do próprio usuário (ADR-026). Cada usuário só lê e altera as suas."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db.models import User
from app.deps import get_db
from app.identity.principal import Principal, get_principal
from app.shared.errors import not_found

router = APIRouter(prefix="/api/v1", tags=["preferences"])

Theme = Literal["auto", "claro", "codigo", "escuro"]
DEFAULT_THEME: Theme = "auto"


class PreferencesIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    theme: Theme


def _view(user: User) -> dict[str, Any]:
    return {"theme": user.ui_theme or DEFAULT_THEME}


@router.get("/me/preferences")
def get_preferences(
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    user = db.get(User, principal.user_id)
    if user is None:
        raise not_found("Usuário")
    return _view(user)


@router.put("/me/preferences")
def put_preferences(
    body: PreferencesIn,
    principal: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    user = db.get(User, principal.user_id)
    if user is None:
        raise not_found("Usuário")
    user.ui_theme = body.theme
    db.commit()
    return _view(user)
