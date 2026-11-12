from __future__ import annotations

import copy

import pytest
import yaml
from app.db.models import AuditEvent, LabStep
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from tests.conftest import ADMIN, ALICE, benign_manifest

pytestmark = pytest.mark.integration


def test_healthz_and_request_id(client: TestClient) -> None:
    r = client.get("/healthz", headers={"X-Request-Id": "req_test_123456"})
    assert r.status_code == 200 and r.headers["X-Request-Id"] == "req_test_123456"
    generated = client.get("/healthz", headers={"X-Request-Id": "bad id with spaces"})
    assert generated.headers["X-Request-Id"].startswith("req_")


def test_register_publishes_release_without_engine_changes(
    client: TestClient, session_factory: sessionmaker[Session]
) -> None:
    r = client.post("/api/v1/admin/lab-releases", json=benign_manifest(), headers=ADMIN)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["labId"] == "LAB-000" and body["status"] == "published"
    assert body["manifestDigest"].startswith("sha256:")
    with session_factory() as db:
        refs = db.execute(select(LabStep.validator_ref).order_by(LabStep.position)).scalars().all()
        assert refs == ["benign/answer/whoami-v1", "benign/python-http/edit-page-v1"]
        actions = db.execute(select(AuditEvent.action)).scalars().all()
    assert "lab_release.published" in actions


def test_register_accepts_yaml(client: TestClient) -> None:
    r = client.post(
        "/api/v1/admin/lab-releases",
        content=yaml.safe_dump(benign_manifest()),
        headers={**ADMIN, "Content-Type": "application/yaml"},
    )
    assert r.status_code == 201, r.text


def test_register_is_idempotent_by_digest(client: TestClient, registered: dict[str, object]) -> None:
    again = client.post("/api/v1/admin/lab-releases", json=benign_manifest(), headers=ADMIN)
    assert again.status_code == 200
    assert again.json()["manifestDigest"] == registered["manifestDigest"]


def test_published_release_is_immutable(client: TestClient, registered: dict[str, object]) -> None:
    changed = benign_manifest()
    changed["metadata"]["title"] = "Título alterado"
    r = client.post("/api/v1/admin/lab-releases", json=changed, headers=ADMIN)
    assert r.status_code == 409 and r.json()["error"]["code"] == "RELEASE_IMMUTABLE"


def test_invalid_manifest_returns_localized_issues(client: TestClient) -> None:
    bad = benign_manifest()
    bad["variants"][0]["resources"]["cpuMillicores"] = 9000
    r = client.post("/api/v1/admin/lab-releases", json=bad, headers=ADMIN)
    assert r.status_code == 400
    err = r.json()["error"]
    assert err["code"] == "VALIDATION_ERROR" and err["requestId"]
    assert err["details"]["issues"][0]["loc"] == "variants.0.resources.cpuMillicores"


@pytest.mark.parametrize(("headers", "status"), [({}, 401), (ALICE, 403)])
def test_only_admin_registers(client: TestClient, headers: dict[str, str], status: int) -> None:
    r = client.post("/api/v1/admin/lab-releases", json=benign_manifest(), headers=headers)
    assert r.status_code == status


def test_unsupported_media_type(client: TestClient) -> None:
    r = client.post(
        "/api/v1/admin/lab-releases", content="x", headers={**ADMIN, "Content-Type": "text/plain"}
    )
    assert r.status_code == 415


def test_public_view_hides_protected_data(client: TestClient, registered: dict[str, object]) -> None:
    for r in (
        client.get("/api/v1/labs", headers=ALICE),
        client.get("/api/v1/labs/LAB-000/releases/0.2.0", headers=ALICE),
    ):
        assert r.status_code == 200
        text = r.text
        assert "validatorRef" not in text and "whoami-v1" not in text
        assert "whoami mostra" not in text  # texto de dica
    assert client.get("/api/v1/labs/LAB-000/releases/9.9.9", headers=ALICE).status_code == 404


def test_new_version_coexists(client: TestClient, registered: dict[str, object]) -> None:
    v2 = copy.deepcopy(benign_manifest())
    v2["metadata"]["version"] = "0.3.0"
    assert client.post("/api/v1/admin/lab-releases", json=v2, headers=ADMIN).status_code == 201
    versions = sorted(i["version"] for i in client.get("/api/v1/labs", headers=ALICE).json()["items"])
    assert versions == ["0.2.0", "0.3.0"]


def test_unknown_validator_is_rejected(client: TestClient) -> None:
    m = copy.deepcopy(benign_manifest())
    m["steps"][0]["validatorRef"] = "benign/answer/does-not-exist-v1"
    r = client.post("/api/v1/admin/lab-releases", json=m, headers=ADMIN)
    assert r.status_code == 400
    assert r.json()["error"]["details"]["issues"][0]["code"] == "UNKNOWN_VALIDATOR"
