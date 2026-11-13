from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml
from alembic import command
from alembic.config import Config
from app.config import AppEnv, AuthMode, Settings
from app.db.engine import make_engine, make_session_factory
from app.main import create_app
from app.runtime.fake import FakeRuntimeAdapter
from app.workers.provisioner import WorkerContext, run_once
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parents[1]
BENIGN_MANIFEST = ROOT / "laboratories" / "LAB-000-hello-benign" / "manifest.yaml"
TABLES = (
    "hint_usages",
    "step_submissions",
    "step_progress",
    "audit_events",
    "jobs",
    "runtime_instances",
    "lab_sessions",
    "lab_attempts",
    "step_hints",
    "lab_steps",
    "lab_variants",
    "lab_releases",
    "labs",
    "users",
)


GATEWAY_SECRET = "test-only-gateway-secret-0123456789abcdef"


class FakeClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self.current

    def advance(self, **kw: float) -> None:
        self.current += timedelta(**kw)


def _db_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = _db_url()
    if not url:
        pytest.skip("TEST_DATABASE_URL não definida: testes de integração exigem PostgreSQL real")
    eng = make_engine(url)
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.attributes["database_url"] = url
    command.upgrade(cfg, "head")
    yield eng
    eng.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> Iterator[sessionmaker[Session]]:
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(TABLES)} CASCADE"))
    yield make_session_factory(engine)


@pytest.fixture
def settings() -> Settings:
    s = Settings(
        app_env=AppEnv.TEST,
        auth_mode=AuthMode.DEV,
        database_url=_db_url() or "unset",
        runtime_adapter="fake",
        log_level="INFO",
        worker_poll_seconds=0.01,
        worker_lease_seconds=30,
        job_max_attempts=3,
        provision_timeout_seconds=120,
        reconcile_interval_seconds=1,
        gateway_ticket_secret=GATEWAY_SECRET,
    )
    s.check()
    return s


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def client(
    settings: Settings, engine: Engine, session_factory: sessionmaker[Session], clock: FakeClock
) -> Iterator[TestClient]:
    app = create_app(settings, engine=engine, session_factory=session_factory, clock=clock)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def runtime() -> FakeRuntimeAdapter:
    return FakeRuntimeAdapter()


@pytest.fixture
def worker(
    session_factory: sessionmaker[Session], runtime: FakeRuntimeAdapter, clock: FakeClock, settings: Settings
) -> WorkerContext:
    return WorkerContext(
        session_factory=session_factory,
        runtime=runtime,
        clock=clock,
        worker_id="worker-a",
        lease=timedelta(seconds=settings.worker_lease_seconds),
        job_max_attempts=settings.job_max_attempts,
    )


def drain(ctx: WorkerContext, limit: int = 50) -> int:
    """Processa jobs disponíveis até esvaziar a fila (no instante atual do relógio)."""
    n = 0
    while n < limit and run_once(ctx):
        n += 1
    return n


def other_worker(ctx: WorkerContext, worker_id: str) -> WorkerContext:
    return replace(ctx, worker_id=worker_id)


ADMIN = {"X-Dev-User": "admin-1", "X-Dev-Roles": "admin"}
ALICE = {"X-Dev-User": "alice", "X-Dev-Roles": "student"}
BOB = {"X-Dev-User": "bob", "X-Dev-Roles": "student"}


def benign_manifest() -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load(BENIGN_MANIFEST.read_text(encoding="utf-8"))
    return data


@pytest.fixture
def registered(client: TestClient) -> dict[str, Any]:
    r = client.post("/api/v1/admin/lab-releases", json=benign_manifest(), headers=ADMIN)
    assert r.status_code == 201, r.text
    body: dict[str, Any] = r.json()
    return body


SESSION_BODY = {"labId": "LAB-000", "version": "0.2.1", "variantId": "python-http"}


def create_session(
    client: TestClient, headers: dict[str, str], key: str = "key-0000001", body: dict[str, str] | None = None
) -> Any:
    return client.post(
        "/api/v1/sessions", json=body or SESSION_BODY, headers={**headers, "Idempotency-Key": key}
    )
