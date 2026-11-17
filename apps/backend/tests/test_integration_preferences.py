"""Preferência de aparência do usuário (ADR-026)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.conftest import ALICE, BOB

pytestmark = pytest.mark.integration


def test_theme_defaults_to_auto_and_is_per_user(client: TestClient) -> None:
    assert client.get("/api/v1/me/preferences", headers=ALICE).json() == {"theme": "auto"}
    r = client.put("/api/v1/me/preferences", json={"theme": "codigo"}, headers=ALICE)
    assert r.status_code == 200 and r.json() == {"theme": "codigo"}
    assert client.get("/api/v1/me/preferences", headers=ALICE).json() == {"theme": "codigo"}
    # Outro usuário não é afetado.
    assert client.get("/api/v1/me/preferences", headers=BOB).json() == {"theme": "auto"}


def test_theme_rejects_unknown_values_and_requires_auth(client: TestClient) -> None:
    assert client.put("/api/v1/me/preferences", json={"theme": "rosa"}, headers=ALICE).status_code in (
        400,
        422,
    )
    assert client.put(
        "/api/v1/me/preferences", json={"theme": "escuro", "x": 1}, headers=ALICE
    ).status_code in (
        400,
        422,
    )
    assert client.get("/api/v1/me/preferences").status_code == 401


def test_theme_accepts_auto(client: TestClient) -> None:
    client.put("/api/v1/me/preferences", json={"theme": "escuro"}, headers=ALICE)
    r = client.put("/api/v1/me/preferences", json={"theme": "auto"}, headers=ALICE)
    assert r.status_code == 200 and r.json() == {"theme": "auto"}
