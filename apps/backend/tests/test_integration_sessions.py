from __future__ import annotations

import copy
import threading
import uuid
from datetime import timedelta
from typing import Any

import pytest
from app.db.models import AuditEvent, Job, LabSession, RuntimeInstance
from app.identity.principal import Principal, Role, _ensure_user
from app.jobs import queue
from app.runtime.fake import FakeRuntimeAdapter
from app.runtime.port import ProvisionRequest, ResourceLimits
from app.sessions import service
from app.shared.errors import ApiError
from app.workers.provisioner import WorkerContext
from app.workers.reconciler import reconcile_once
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from tests.conftest import (
    ADMIN,
    ALICE,
    BOB,
    SESSION_BODY,
    FakeClock,
    benign_manifest,
    create_session,
    drain,
)

pytestmark = pytest.mark.integration


def status_of(client: TestClient, sid: str, headers: dict[str, str] = ALICE) -> str:
    r = client.get(f"/api/v1/sessions/{sid}", headers=headers)
    assert r.status_code == 200, r.text
    value: str = r.json()["status"]
    return value


def actions_for(session_factory: sessionmaker[Session], sid: str) -> list[str]:
    with session_factory() as db:
        return list(
            db.execute(
                select(AuditEvent.action).where(AuditEvent.resource_id == sid).order_by(AuditEvent.seq)
            ).scalars()
        )


# --- criação e idempotência (FR-020/022, ENG-01) ---------------------------------------------


def test_create_returns_202_requested(client: TestClient, registered: dict[str, Any]) -> None:
    r = create_session(client, ALICE)
    assert r.status_code == 202, r.text
    body = r.json()
    assert body["status"] == "REQUESTED" and body["variantId"] == "python-http"
    assert r.headers["Location"] == f"/api/v1/sessions/{body['sessionId']}"
    assert "runtime" not in r.text.lower()  # nenhum ref/URL interna exposta


def test_same_key_same_body_replays(client: TestClient, registered: dict[str, Any]) -> None:
    a = create_session(client, ALICE).json()
    r = create_session(client, ALICE)
    assert r.status_code == 202 and r.json()["sessionId"] == a["sessionId"]
    assert r.headers["Idempotent-Replayed"] == "true"


def test_same_key_different_body_conflicts(client: TestClient, registered: dict[str, Any]) -> None:
    v2 = copy.deepcopy(benign_manifest())
    v2["metadata"]["version"] = "0.3.0"
    client.post("/api/v1/admin/lab-releases", json=v2, headers=ADMIN)
    create_session(client, ALICE)
    r = create_session(client, ALICE, body={**SESSION_BODY, "version": "0.3.0"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_second_active_session_for_same_release_conflicts(
    client: TestClient, registered: dict[str, Any]
) -> None:
    first = create_session(client, ALICE).json()
    r = create_session(client, ALICE, key="key-0000002")
    assert r.status_code == 409
    err = r.json()["error"]
    assert err["code"] == "SESSION_ALREADY_ACTIVE" and err["details"]["sessionId"] == first["sessionId"]


def test_same_key_is_scoped_per_user(client: TestClient, registered: dict[str, Any]) -> None:
    a = create_session(client, ALICE).json()
    b = create_session(client, BOB).json()
    assert a["sessionId"] != b["sessionId"]


@pytest.mark.parametrize(
    ("key", "body", "status"),
    [
        (None, SESSION_BODY, 400),
        ("short", SESSION_BODY, 400),
        ("key-0000001", {**SESSION_BODY, "labId": "LAB-999"}, 404),
        ("key-0000001", {**SESSION_BODY, "variantId": "node-x"}, 404),
        ("key-0000001", {**SESSION_BODY, "extra": "x"}, 400),
        ("key-0000001", {**SESSION_BODY, "labId": "../etc"}, 400),
    ],
)
def test_create_rejections(
    client: TestClient, registered: dict[str, Any], key: str | None, body: dict[str, str], status: int
) -> None:
    headers = dict(ALICE)
    if key is not None:
        headers["Idempotency-Key"] = key
    r = client.post("/api/v1/sessions", json=body, headers=headers)
    assert r.status_code == status, r.text
    assert "error" in r.json()


def test_unauthenticated_is_401(client: TestClient, registered: dict[str, Any]) -> None:
    assert (
        client.post(
            "/api/v1/sessions", json=SESSION_BODY, headers={"Idempotency-Key": "key-0000001"}
        ).status_code
        == 401
    )


def _concurrent_create(session_factory: sessionmaker[Session], keys: list[str]) -> list[Any]:
    with session_factory() as db:
        uid = _ensure_user(db, "alice")
    principal = Principal(uid, "alice", frozenset({Role.STUDENT}))
    cmd = service.CreateSessionCommand("LAB-000", "0.2.1", "python-http")
    barrier = threading.Barrier(len(keys))
    results: list[Any] = [None] * len(keys)

    def worker(i: int) -> None:
        barrier.wait()
        with session_factory() as db:
            try:
                res = service.create_session(
                    db,
                    principal=principal,
                    cmd=cmd,
                    idempotency_key=keys[i],
                    now=FakeClock().now(),
                    max_attempts=3,
                    provision_timeout=timedelta(seconds=60),
                )
                results[i] = str(res.session.id)
            except ApiError as exc:
                results[i] = exc.code

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(keys))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_eng01_20_concurrent_same_key_create_one_session(
    session_factory: sessionmaker[Session], registered: dict[str, Any]
) -> None:
    results = _concurrent_create(session_factory, ["same-key-123"] * 20)
    assert len(set(results)) == 1 and uuid.UUID(results[0])
    with session_factory() as db:
        assert db.execute(select(func.count()).select_from(LabSession)).scalar_one() == 1
        assert db.execute(select(func.count()).select_from(Job)).scalar_one() == 1


def test_concurrent_different_keys_create_one_active_session(
    session_factory: sessionmaker[Session], registered: dict[str, Any]
) -> None:
    results = _concurrent_create(session_factory, [f"key-{i:08d}" for i in range(10)])
    ids = [r for r in results if r != "SESSION_ALREADY_ACTIVE"]
    assert len(ids) == 1 and results.count("SESSION_ALREADY_ACTIVE") == 9
    with session_factory() as db:
        assert db.execute(select(func.count()).select_from(Job)).scalar_one() == 1


# --- ownership (FR-002, ENG-03/SEC-01 na API) --------------------------------------------------


def test_other_user_cannot_see_or_terminate(client: TestClient, registered: dict[str, Any]) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    for r in (
        client.get(f"/api/v1/sessions/{sid}", headers=BOB),
        client.delete(f"/api/v1/sessions/{sid}", headers=BOB),
    ):
        assert r.status_code == 404
        assert sid not in r.text
    assert status_of(client, sid) == "REQUESTED"
    assert client.get(f"/api/v1/sessions/{uuid.uuid4()}", headers=ALICE).status_code == 404
    assert client.get("/api/v1/sessions/not-a-uuid", headers=ALICE).status_code == 400


def test_admin_can_inspect_and_terminate(client: TestClient, registered: dict[str, Any]) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    assert client.get(f"/api/v1/sessions/{sid}", headers=ADMIN).status_code == 200
    assert client.delete(f"/api/v1/sessions/{sid}", headers=ADMIN).json()["status"] == "TERMINATING"


# --- ciclo de vida ponta a ponta -------------------------------------------------------------


def test_full_lifecycle_ready_then_terminated(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    session_factory: sessionmaker[Session],
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    assert status_of(client, sid) == "READY"
    assert [o.session_id for o in runtime.list_owned()] == [sid]

    r = client.delete(f"/api/v1/sessions/{sid}", headers=ALICE)
    assert r.status_code == 202 and r.json()["status"] == "TERMINATING"
    again = client.delete(f"/api/v1/sessions/{sid}", headers=ALICE)
    assert again.status_code == 202
    with session_factory() as db:
        assert (
            db.execute(select(func.count()).select_from(Job).where(Job.kind == "TERMINATE")).scalar_one() == 1
        )
    drain(worker)
    assert status_of(client, sid) == "TERMINATED"
    assert runtime.list_owned() == []
    with session_factory() as db:
        inst = db.execute(select(RuntimeInstance)).scalar_one()
        assert inst.status == "ABSENT" and inst.terminated_at is not None
    assert actions_for(session_factory, sid) == [
        "session.requested",
        "session.provisioning",
        "session.ready",
        "session.terminating",
        "session.terminated",
    ]
    # Reabrir após término é permitido (sessão anterior não conta como ativa).
    assert create_session(client, ALICE, key="key-0000009").status_code == 202


def test_readiness_polling(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
) -> None:
    runtime.faults.ready_after_polls = 2
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    assert status_of(client, sid) == "PROVISIONING"
    for _ in range(3):
        clock.advance(seconds=2)
        drain(worker)
    assert status_of(client, sid) == "READY"
    assert len(runtime.list_owned()) == 1


def test_transient_failure_is_retried(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
) -> None:
    runtime.faults.provision.extend(["transient"])
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    assert status_of(client, sid) == "PROVISIONING"
    clock.advance(seconds=5)
    drain(worker)
    assert status_of(client, sid) == "READY"


def test_exhausted_retries_fail_closed_and_clean_up(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
) -> None:
    runtime.faults.provision.extend(["transient"] * 3)
    sid = create_session(client, ALICE).json()["sessionId"]
    for _ in range(5):
        drain(worker)
        clock.advance(seconds=30)
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()
    assert body["status"] == "TERMINATED" and body["lastErrorCode"] == "RUNTIME_UNAVAILABLE"
    assert "session.failed" in actions_for(session_factory, sid)
    assert runtime.list_owned() == []


def test_permanent_failure(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, runtime: FakeRuntimeAdapter
) -> None:
    runtime.faults.provision.extend(["permanent"])
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    drain(worker)
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()
    assert body["status"] == "TERMINATED" and body["lastErrorCode"] == "PROVISION_REJECTED"


def test_readiness_timeout_fails(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
) -> None:
    runtime.faults.never_ready = True
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    clock.advance(seconds=121)
    drain(worker)
    drain(worker)
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()
    assert body["status"] == "TERMINATED" and body["lastErrorCode"] == "PROVISION_TIMEOUT"
    assert runtime.list_owned() == []


def test_terminate_before_provisioning_creates_no_runtime(
    client: TestClient, registered: dict[str, Any], worker: WorkerContext, runtime: FakeRuntimeAdapter
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    client.delete(f"/api/v1/sessions/{sid}", headers=ALICE)
    drain(worker)
    assert status_of(client, sid) == "TERMINATED"
    assert ("provision", sid) not in runtime.calls
    assert runtime.list_owned() == []


def test_terminate_retries_on_transient_error(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    runtime.faults.terminate.extend(["transient"])
    client.delete(f"/api/v1/sessions/{sid}", headers=ALICE)
    drain(worker)
    assert status_of(client, sid) == "TERMINATING"
    clock.advance(seconds=5)
    drain(worker)
    assert status_of(client, sid) == "TERMINATED"


# --- falha de worker (ENG-02) ------------------------------------------------------------------


def test_eng02_crashed_worker_lease_is_recovered_without_duplicates(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    with session_factory() as db:  # worker "crashed" captura o job e morre sem concluir
        crashed = queue.claim(db, worker_id="crashed", now=clock.now(), lease=timedelta(seconds=30))
    assert crashed is not None
    assert drain(worker) == 0  # lease ainda válido: ninguém rouba o job
    clock.advance(seconds=31)
    drain(worker)
    assert status_of(client, sid) == "READY"
    assert [c for c in runtime.calls if c[0] == "provision"] == [("provision", sid)]
    assert len(runtime.list_owned()) == 1


# --- TTL, órfãos e reconciliação (FR-025, ENG-06, TM-14) ---------------------------------------


def test_eng06_expired_session_is_cleaned(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
    session_factory: sessionmaker[Session],
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    clock.advance(minutes=14)
    assert reconcile_once(worker).expired == []
    clock.advance(minutes=2)
    report = reconcile_once(worker)
    assert report.expired == [sid]
    assert status_of(client, sid) == "EXPIRED"
    drain(worker)
    assert status_of(client, sid) == "TERMINATED"
    assert runtime.list_owned() == []
    trail = actions_for(session_factory, sid)
    assert trail[-3:] == ["session.expired", "session.terminating", "session.terminated"]


def test_orphan_runtime_is_removed_and_audited(
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    session_factory: sessionmaker[Session],
    clock: FakeClock,
) -> None:
    orphan_sid = str(uuid.uuid4())
    ref = runtime.inject_orphan(
        ProvisionRequest(
            session_id=orphan_sid,
            lab_release="LAB-000@0.2.1",
            variant_id="python-http",
            image_digest="registry.local/labs/x@sha256:" + "ab" * 32,
            runtime_profile="benign-test",
            resources=ResourceLimits(100, 128, 64, 32),
            egress_profile="deny-all",
            exposed_port=8080,
            expires_at=clock.now(),
        )
    )
    report = reconcile_once(worker)
    assert report.orphans_removed == [ref]
    assert runtime.list_owned() == []
    assert actions_for(session_factory, ref) == ["runtime.orphan_removed"]


def test_runtime_created_after_termination_is_reconciled(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    session_factory: sessionmaker[Session],
) -> None:
    """Corrida: provisionamento termina depois de a sessão já estar TERMINATED."""
    sid = create_session(client, ALICE).json()["sessionId"]
    client.delete(f"/api/v1/sessions/{sid}", headers=ALICE)
    drain(worker)
    assert status_of(client, sid) == "TERMINATED"
    with session_factory() as db:
        s = db.get(LabSession, uuid.UUID(sid))
        assert s is not None
        from app.workers.provisioner import build_request

        runtime.provision(build_request(db, s))  # recurso "atrasado" do orquestrador
    assert reconcile_once(worker).orphans_removed == [runtime.ref_for(sid)]
    assert runtime.list_owned() == []


def test_dead_terminate_job_is_requeued(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    clock: FakeClock,
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    runtime.faults.terminate.extend(["transient"] * 3)
    client.delete(f"/api/v1/sessions/{sid}", headers=ALICE)
    for _ in range(4):
        drain(worker)
        clock.advance(seconds=30)
    assert status_of(client, sid) == "TERMINATING"  # job esgotou (dead), sessão não "finge" término
    report = reconcile_once(worker)
    assert report.requeued_terminations == [sid]
    drain(worker)
    assert status_of(client, sid) == "TERMINATED"


# --- imutabilidade de versão (ENG-07) ----------------------------------------------------------


def test_eng07_new_version_does_not_change_existing_session(
    client: TestClient, registered: dict[str, Any]
) -> None:
    sid = create_session(client, ALICE).json()["sessionId"]
    v2 = copy.deepcopy(benign_manifest())
    v2["metadata"]["version"] = "0.3.0"
    v2["variants"][0]["session"]["ttlMinutes"] = 30
    assert client.post("/api/v1/admin/lab-releases", json=v2, headers=ADMIN).status_code == 201
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).json()
    assert body["version"] == "0.2.1"


def test_ready_persists_internal_endpoint_but_api_never_exposes_it(
    client: TestClient,
    registered: dict[str, Any],
    worker: WorkerContext,
    runtime: FakeRuntimeAdapter,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.runtime.port import RuntimeEndpoint

    monkeypatch.setattr(runtime, "endpoint", lambda ref: RuntimeEndpoint("10.89.0.7", 8080))
    sid = create_session(client, ALICE).json()["sessionId"]
    drain(worker)
    assert status_of(client, sid) == "READY"
    with session_factory() as db:
        inst = db.execute(
            select(RuntimeInstance).where(RuntimeInstance.session_id == uuid.UUID(sid))
        ).scalar_one()
        assert (inst.endpoint_host, inst.endpoint_port, inst.status) == ("10.89.0.7", 8080, "READY")
    body = client.get(f"/api/v1/sessions/{sid}", headers=ALICE).text
    assert "10.89.0.7" not in body
