"""Suíte de contrato do RuntimePort (ENG-08). Todo adapter real deve passar por ela.

O adapter Docker local (ADR-008) só roda com ``DOCKER_CONTRACT_TESTS=1`` e Docker acessível;
caso contrário é marcado como *skip* (nunca como sucesso).
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime

import pytest
from app.runtime.fake import FakeRuntimeAdapter
from app.runtime.port import (
    ProvisionRequest,
    ResourceLimits,
    RuntimeConflictError,
    RuntimePhase,
    RuntimePort,
)

from tests.docker_support import docker_lab_image

FAKE_IMAGE = "registry.local/labs/x@sha256:" + "ab" * 32
_IMAGE: dict[str, str] = {}


def _request(session_id: str = "11111111-1111-1111-1111-111111111111") -> ProvisionRequest:
    return ProvisionRequest(
        session_id=session_id,
        lab_release="LAB-000@0.1.0",
        variant_id="python-http",
        image_digest=_IMAGE.get("current", FAKE_IMAGE),
        runtime_profile="benign-test",
        resources=ResourceLimits(100, 128, 64, 32),
        egress_profile="deny-all",
        exposed_port=8080,
        expires_at=datetime(2026, 11, 11, 13, tzinfo=UTC),
        startup_command=("python", "-m", "http.server", "8080", "--bind", "0.0.0.0"),
        workspace_path="/workspace",
    )


@pytest.fixture(params=["fake", "docker"])
def adapter(request: pytest.FixtureRequest) -> Iterator[RuntimePort]:
    if request.param == "fake":
        _IMAGE.pop("current", None)
        yield FakeRuntimeAdapter()
        return
    image = docker_lab_image()
    from app.runtime.docker_local import DockerRuntimeAdapter

    _IMAGE["current"] = image
    rt = DockerRuntimeAdapter()
    try:
        yield rt
    finally:
        for owned in rt.list_owned():
            rt.terminate(owned.runtime_ref)
        _IMAGE.pop("current", None)


def _wait_ready(adapter: RuntimePort, ref: str, timeout: float = 60) -> RuntimePhase:
    deadline = time.monotonic() + timeout
    phase = adapter.inspect(ref).phase
    while phase is RuntimePhase.PENDING and time.monotonic() < deadline:
        time.sleep(0.5)
        phase = adapter.inspect(ref).phase
    return phase


def test_provision_is_idempotent_and_deterministic(adapter: RuntimePort) -> None:
    req = _request()
    ref1 = adapter.provision(req)
    ref2 = adapter.provision(req)
    assert ref1 == ref2 == adapter.ref_for(req.session_id)
    assert len([o for o in adapter.list_owned() if o.session_id == req.session_id]) == 1


def test_divergent_policy_is_a_conflict(adapter: RuntimePort) -> None:
    req = _request()
    adapter.provision(req)
    with pytest.raises(RuntimeConflictError):
        adapter.provision(replace(req, resources=ResourceLimits(200, 128, 64, 32)))


def test_inspect_unknown_is_absent(adapter: RuntimePort) -> None:
    assert adapter.inspect(adapter.ref_for("nope")).phase is RuntimePhase.ABSENT


def test_terminate_is_idempotent_and_confirms_absence(adapter: RuntimePort) -> None:
    ref = adapter.provision(_request())
    adapter.terminate(ref)
    adapter.terminate(ref)
    assert adapter.inspect(ref).phase is RuntimePhase.ABSENT
    assert adapter.list_owned() == []


def test_sessions_are_independent(adapter: RuntimePort) -> None:
    a = adapter.provision(_request("aaaaaaaa-0000-0000-0000-000000000000"))
    b = adapter.provision(_request("bbbbbbbb-0000-0000-0000-000000000000"))
    assert a != b
    adapter.terminate(a)
    assert adapter.inspect(b).phase is not RuntimePhase.ABSENT


def test_becomes_ready(adapter: RuntimePort) -> None:
    ref = adapter.provision(_request())
    assert _wait_ready(adapter, ref) is RuntimePhase.READY
