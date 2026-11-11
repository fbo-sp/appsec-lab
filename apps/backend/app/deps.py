from __future__ import annotations

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session

from app.config import Settings
from app.shared.clock import Clock


def get_db(request: Request) -> Iterator[Session]:
    factory = request.app.state.session_factory
    db: Session = factory()
    try:
        yield db
    finally:
        db.close()


def get_clock(request: Request) -> Clock:
    clock: Clock = request.app.state.clock
    return clock


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings
