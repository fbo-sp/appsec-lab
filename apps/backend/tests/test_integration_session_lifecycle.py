"""ADR-011: tempo de provisionamento registrado, indicadores do admin e renovação do prazo da sessão."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.db.models import AuditEvent, LabSession
from app.workers.provisioner import WorkerContext
from app.workers.reconciler import reconcile_once
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from tests.conftest import ADMIN, ALICE, BOB, FakeClock, create_session, drain


def _ready(client: TestClient, worker: WorkerContext, clock: FakeClock, key: str = "key-0000001") -> str:
    sid: str = create_session(client, ALICE, key=key).json()["sessionId"]
    clock.advance(seconds=7)
    drain(worker)
    return sid


def _renew(client: TestClient, sid: str, headers: dict[str, str] = ALICE) -> Any:
    return client.post(f"/api/v1/sessions/{sid}/renewals", headers=headers)


def test_ready_records_provisioning_time(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
) -> None:
    sid = _ready(client, worker, clock)
    with session_factory() as db:
        s = db.get(LabSession, sid)
        assert s is not None and s.status == "READY"
        assert s.provision_ms is not None and s.provision_ms >= 7000 and s.ready_at == clock.now()


def test_provisioning_metrics_admin_only(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, clock: FakeClock
) -> None:
    _ready(client, worker, clock)
    assert client.get("/api/v1/admin/metrics/provisioning", headers=ALICE).status_code == 403
    r = client.get("/api/v1/admin/metrics/provisioning", headers=ADMIN)
    assert r.status_code == 200, r.text
    [item] = r.json()["items"]
    assert item["labId"] == "LAB-000" and item["variantId"] == "python-http"
    assert item["sessions"] == 1 and item["ready"] == 1 and item["failed"] == 0
    assert item["provisionSeconds"]["p50"] >= 7 and item["provisionSeconds"]["max"] >= 7


def test_session_view_exposes_renewal_policy(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, clock: FakeClock
) -> None:
    sid = _ready(client, worker, clock)
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()
    assert body["ttlMinutes"] == 15 and body["renewals"] == 0 and body["maxRenewals"] == 2
    expires = datetime.fromisoformat(body["expiresAt"])
    assert datetime.fromisoformat(body["renewableAt"]) == expires - timedelta(minutes=5)


def test_renewal_window_limit_and_audit(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
) -> None:
    sid = _ready(client, worker, clock)
    r = _renew(client, sid)
    assert r.status_code == 409 and r.json()["error"]["code"] == "RENEWAL_TOO_EARLY"
    assert _renew(client, sid, headers=BOB).status_code == 404
    for n in (1, 2):
        clock.advance(minutes=11)
        r = _renew(client, sid)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["renewals"] == n
        assert datetime.fromisoformat(body["expiresAt"]) == clock.now() + timedelta(minutes=15)
    assert r.json()["renewableAt"] is None
    clock.advance(minutes=11)
    r = _renew(client, sid)
    assert r.status_code == 409 and r.json()["error"]["code"] == "RENEWAL_LIMIT_REACHED"
    with session_factory() as db:
        assert len(db.execute(select(AuditEvent).where(AuditEvent.action == "session.renewed")).all()) == 2


def test_expired_session_cannot_be_renewed_and_is_reclaimed(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, clock: FakeClock
) -> None:
    sid = _ready(client, worker, clock)
    clock.advance(minutes=16)
    r = _renew(client, sid)
    assert r.status_code == 409 and r.json()["error"]["code"] == "SESSION_NOT_READY"
    reconcile_once(worker)
    drain(worker)
    assert client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()["status"] in ("EXPIRED", "TERMINATED")


def test_renewal_keeps_session_alive_past_original_deadline(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, clock: FakeClock
) -> None:
    sid = _ready(client, worker, clock)
    clock.advance(minutes=12)
    assert _renew(client, sid).status_code == 200
    clock.advance(minutes=6)  # passou do prazo original (15 min), mas dentro do renovado
    reconcile_once(worker)
    assert client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()["status"] == "READY"
