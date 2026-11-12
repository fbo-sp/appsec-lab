"""App factory do plano de controle (monólito modular)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.catalog.router import router as catalog_router
from app.config import AuthMode, Settings
from app.db.engine import make_engine, make_session_factory
from app.identity.principal import dev_principal
from app.sessions.router import router as sessions_router
from app.shared.clock import Clock, SystemClock
from app.shared.errors import install_error_handlers
from app.shared.logging import configure_logging
from app.shared.middleware import install_correlation_middleware


def create_app(
    settings: Settings | None = None,
    *,
    engine: Engine | None = None,
    session_factory: sessionmaker[Session] | None = None,
    clock: Clock | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.check()
    configure_logging(settings.log_level)
    engine = engine or make_engine(settings.database_url)
    app = FastAPI(
        title="CECyber AppSec Labs - Control Plane",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.state.settings = settings
    app.state.session_factory = session_factory or make_session_factory(engine)
    app.state.clock = clock or SystemClock()
    if settings.auth_mode is AuthMode.DEV:
        app.state.authenticator = dev_principal
    install_correlation_middleware(app)
    install_error_handlers(app)
    app.include_router(catalog_router)
    app.include_router(sessions_router)

    @app.get("/healthz", tags=["ops"])
    def healthz() -> dict[str, Any]:
        with app.state.session_factory() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok"}

    return app


def app_factory() -> FastAPI:  # uvicorn --factory app.main:app_factory
    return create_app()
