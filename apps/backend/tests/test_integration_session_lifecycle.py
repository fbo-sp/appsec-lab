"""ADR-011: tempo de provisionamento registrado, indicadores do admin e renovação do prazo da sessão."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest
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


# --- ADR-014: tempo de uso por sessão (capacidade) ---------------------------------------------------


def test_session_usage_records_end_and_reason(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
) -> None:
    from app.sessions.service import usage_seconds

    terminated = _ready(client, worker, clock)
    clock.advance(minutes=10)
    assert client.delete(f"/api/v1/sessions/{terminated}", headers=ALICE).status_code == 202
    expired = _ready(client, worker, clock, key="key-0000002")
    clock.advance(minutes=40)  # o worker só percebe bem depois do prazo de 15 min
    reconcile_once(worker)
    drain(worker)
    with session_factory() as db:
        t = db.get(LabSession, terminated)
        e = db.get(LabSession, expired)
        assert t is not None and e is not None
        assert t.end_reason == "request_termination" and usage_seconds(t, clock.now()) == 600
        # A expiração conta até o prazo, não até o instante em que o worker a detectou.
        assert e.end_reason == "expire" and e.ended_at == e.expires_at
        assert usage_seconds(e, clock.now()) == 15 * 60 - 7  # pronta 7 s após a criação
    [item] = client.get("/api/v1/admin/metrics/provisioning", headers=ADMIN).json()["items"]
    assert item["usageMinutes"]["ended"] == 2 and item["usageMinutes"]["max"] == 14.88
    assert item["usageMinutes"]["p50"] == 12.44
    assert item["endReasons"] == {"expired": 1, "terminated": 1}


# --- ADR-014: inatividade e minutos ativos ------------------------------------------------------------


def _activity(client: TestClient, sid: str, headers: dict[str, str] = ALICE) -> Any:
    return client.post(f"/api/v1/sessions/{sid}/activity", headers=headers)


def test_idle_session_is_terminated_and_activity_postpones_it(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.sessions import service as sessions

    monkeypatch.setattr(sessions, "IDLE_MINUTES", 5)  # prazo da variante de teste é 15 min
    sid = _ready(client, worker, clock)
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()
    assert body["idleMinutes"] == 5
    assert datetime.fromisoformat(body["idleDeadline"]) == clock.now() + timedelta(minutes=5)
    clock.advance(minutes=4)
    assert _activity(client, sid, headers=BOB).status_code == 404  # só o dono sinaliza atividade
    r = _activity(client, sid)
    deadline = datetime.fromisoformat(r.json()["idleDeadline"])
    assert r.status_code == 200 and deadline == clock.now() + timedelta(minutes=5)
    clock.advance(minutes=4)
    assert reconcile_once(worker).idle == []
    assert client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()["status"] == "READY"
    clock.advance(minutes=2)
    assert reconcile_once(worker).idle == [sid]
    drain(worker)
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()
    assert body["status"] in ("TERMINATING", "TERMINATED") and body["endReason"] == "idle"
    with session_factory() as db:
        ev = db.execute(
            select(AuditEvent).where(
                AuditEvent.action == "session.terminating", AuditEvent.resource_id == sid
            )
        ).scalar_one()
        assert ev.event_metadata["reason"] == "idle"


def test_active_minutes_count_distinct_minutes_across_sessions(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, clock: FakeClock
) -> None:
    sid = _ready(client, worker, clock)
    client.get(f"/api/v1/sessions/{sid}/steps", headers=ALICE)  # cria a tentativa
    _activity(client, sid)
    clock.advance(seconds=20)
    _activity(client, sid)  # mesmo minuto: não soma de novo
    clock.advance(minutes=1)
    _activity(client, sid)
    clock.advance(minutes=10)  # parado: não conta
    assert client.delete(f"/api/v1/sessions/{sid}", headers=ALICE).status_code == 202
    drain(worker)
    sid2 = _ready(client, worker, clock, key="key-0000002")
    _activity(client, sid2)
    att = client.get(f"/api/v1/sessions/{sid2}/steps", headers=ALICE).json()["attempt"]
    assert att["activeMinutes"] == 3 and att["sessions"] == 2
