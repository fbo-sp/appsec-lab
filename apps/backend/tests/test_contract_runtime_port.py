"""Suíte de contrato do RuntimePort (ENG-08). Todo adapter real deve passar por ela."""

from __future__ import annotations

from collections.abc import Callable
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

ADAPTERS: list[Callable[[], RuntimePort]] = [FakeRuntimeAdapter]


def _request(session_id: str = "11111111-1111-1111-1111-111111111111") -> ProvisionRequest:
    return ProvisionRequest(
        session_id=session_id,
        lab_release="LAB-000@0.1.0",
        variant_id="python-http",
        image_digest="registry.local/labs/x@sha256:" + "ab" * 32,
        runtime_profile="benign-test",
        resources=ResourceLimits(100, 128, 64, 32),
        egress_profile="deny-all",
        exposed_port=8080,
        expires_at=datetime(2026, 11, 11, 13, tzinfo=UTC),
    )


@pytest.fixture(params=ADAPTERS, ids=lambda f: getattr(f, "__name__", str(f)))
def adapter(request: pytest.FixtureRequest) -> RuntimePort:
    factory: Callable[[], RuntimePort] = request.param
    return factory()


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
    phases = {adapter.inspect(ref).phase for _ in range(5)}
    assert RuntimePhase.READY in phases
