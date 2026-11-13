"""Emissão de tickets do gateway, etapas e listagem de sessões (IMP-302/303)."""

from __future__ import annotations

from dataclasses import replace
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
from app.config import Settings
from app.db.models import AuditEvent
from app.gateway.tickets import Audience, Purpose, verify
from app.main import create_app
from app.workers.provisioner import WorkerContext
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, sessionmaker

from tests.conftest import ADMIN, ALICE, BOB, GATEWAY_SECRET, FakeClock, create_session, drain

pytestmark = pytest.mark.integration


def _ready(client: TestClient, worker: WorkerContext) -> str:
    sid: str = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    return sid


def _ticket(client: TestClient, sid: str, purpose: str = "workspace", headers: dict[str, str] = ALICE) -> Any:
    return client.post(f"/api/v1/sessions/{sid}/gateway-ticket", json={"purpose": purpose}, headers=headers)


def test_owner_gets_single_use_ticket_and_session_becomes_active(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
) -> None:
    sid = _ready(client, worker)
    r = _ticket(client, sid)
    assert r.status_code == 200 and r.headers["Cache-Control"] == "no-store"
    url = urlparse(r.json()["url"])
    assert url.netloc == "127.0.0.1:8001" and url.path == f"/s/{sid}/__cecyber/auth"
    token = parse_qs(url.query)["ticket"][0]
    claims = verify(GATEWAY_SECRET, token, aud=Audience.TICKET, purpose=Purpose.WORKSPACE, now=clock.now())
    assert claims.sid == sid
    assert client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()["status"] == "ACTIVE"

    pv = _ticket(client, sid, "preview").json()["url"]
    assert pv.startswith("http://127.0.0.1:8002/__cecyber/auth?ticket=")
    with session_factory() as db:
        events = db.execute(
            select(AuditEvent).where(AuditEvent.action == "session.gateway_ticket_issued")
        ).scalars()
        metas = [e.event_metadata for e in events]
    assert [m["purpose"] for m in metas] == ["workspace", "preview"]
    assert all(token not in str(m) for m in metas)  # token nunca é auditado/logado


def test_ticket_denied_to_other_users_and_admin(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext
) -> None:
    sid = _ready(client, worker)
    assert _ticket(client, sid, headers=BOB).status_code == 404
    # Admin enxerga a sessão para operação, mas não entra no workspace do aluno.
    assert _ticket(client, sid, headers=ADMIN).status_code == 404


def test_ticket_requires_ready_session(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    r = _ticket(client, sid)
    assert r.status_code == 409 and r.json()["error"]["code"] == "SESSION_NOT_READY"
    drain(worker)
    client.delete(f"/api/v1/sessions/{sid}", headers=ALICE)
    assert _ticket(client, sid).status_code == 409


def test_ticket_rejects_expired_session(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, clock: FakeClock
) -> None:
    sid = _ready(client, worker)
    clock.advance(minutes=16)
    assert _ticket(client, sid).status_code == 409


def test_invalid_purpose_is_validation_error(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext
) -> None:
    sid = _ready(client, worker)
    assert _ticket(client, sid, "admin").status_code in (400, 422)


def test_gateway_unconfigured_returns_503(
    settings: Settings,
    engine: Engine,
    session_factory: sessionmaker[Session],
    clock: FakeClock,
    registered: dict[str, Any],
    worker: WorkerContext,
    client: TestClient,
) -> None:
    sid = _ready(client, worker)
    app = create_app(
        replace(settings, gateway_ticket_secret=None),
        engine=engine,
        session_factory=session_factory,
        clock=clock,
    )
    with TestClient(app) as c:
        assert _ticket(c, sid).status_code == 503


def test_steps_expose_only_first_step_details(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext
) -> None:
    sid = _ready(client, worker)
    r = client.get(f"/api/v1/sessions/{sid}/steps", headers=ALICE)
    assert r.status_code == 200
    items = r.json()["items"]
    assert items[0]["status"] == "AVAILABLE" and items[0]["task"]
    body = r.text
    assert "validatorRef" not in body and "benign/" not in body
    # Dicas: só a contagem antes da revelação; etapa bloqueada não expõe enunciado.
    assert items[0]["hints"] == {"available": 2, "revealed": [], "nextCost": 0}
    assert "task" not in items[1] and "hints" not in items[1] and items[1]["status"] == "LOCKED"
    assert client.get(f"/api/v1/sessions/{sid}/steps", headers=BOB).status_code == 404


def test_list_own_sessions(client: TestClient, registered: dict[str, Any], worker: WorkerContext) -> None:
    sid = _ready(client, worker)
    assert [s["sessionId"] for s in client.get("/api/v1/sessions", headers=ALICE).json()["items"]] == [sid]
    assert client.get("/api/v1/sessions", headers=BOB).json()["items"] == []
