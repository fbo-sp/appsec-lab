"""DockerEvaluator LOCAL (ADR-010) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

Comprova: snapshot do workspace, execução numa cópia isolada (fora do workspace editável), probe
confiável, resultado por critério, falha técnica => erro (nunca aprovação) e limpeza dos recursos.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

import pytest
from app.runtime.port import ProvisionRequest, ResourceLimits, RuntimePhase
from app.validation.port import EvaluationRequest
from app.validation.suites import HttpSuite, get_suite

from tests.docker_support import docker_lab_image

SUITE_REF = "benign/python-http/edit-page-v1"
CMD = ("python", "-m", "http.server", "8080", "--bind", "0.0.0.0")


@pytest.fixture
def env() -> Iterator[tuple[Any, Any, str]]:
    image = docker_lab_image()
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    try:
        yield rt, DockerEvaluator(), image
    finally:
        for owned in rt.list_owned():
            rt.terminate(owned.runtime_ref)


def _provision(rt: Any, image: str) -> Any:
    sid = str(uuid.uuid4())
    ref = rt.provision(
        ProvisionRequest(
            session_id=sid,
            lab_release="LAB-000@0.2.1",
            variant_id="python-http",
            image_digest=image,
            runtime_profile="benign-test",
            resources=ResourceLimits(250, 128, 64, 64),
            egress_profile="deny-all",
            exposed_port=8080,
            expires_at=datetime(2030, 1, 1, tzinfo=UTC),
            startup_command=CMD,
            workspace_path="/workspace",
        )
    )
    deadline = time.monotonic() + 60
    while rt.inspect(ref).phase is RuntimePhase.PENDING and time.monotonic() < deadline:
        time.sleep(0.5)
    assert rt.inspect(ref).phase is RuntimePhase.READY
    return rt._client.containers.get(ref), ref


def _request(ref: str, image: str) -> EvaluationRequest:
    suite = get_suite(SUITE_REF)
    assert isinstance(suite, HttpSuite)
    return EvaluationRequest(
        submission_id=str(uuid.uuid4()),
        runtime_ref=ref,
        image_digest=image,
        workspace_path="/workspace",
        startup_command=CMD,
        app_port=8080,
        checks=[
            {
                "id": c.id,
                "path": c.path,
                "method": c.method,
                "form": c.form,
                "expect_status": c.expect_status,
                "contains": list(c.contains),
                "not_contains": list(c.not_contains),
            }
            for c in suite.checks
        ],
        cpu_millicores=250,
        memory_mib=128,
        pids_max=64,
        timeout_seconds=60,
    )


def _leftovers(rt: Any, submission_id: str) -> list[str]:
    from app.validation.docker_eval import EVAL_LABEL

    flt = {"label": f"{EVAL_LABEL}={submission_id}"}
    c = rt._client
    return (
        [x.name for x in c.containers.list(all=True, filters=flt)]
        + [x.name for x in c.networks.list(filters=flt)]
        + [x.name for x in c.volumes.list(filters=flt)]
    )


def test_unedited_workspace_fails_greeting_criterion(env: tuple[Any, Any, str]) -> None:
    rt, ev, image = env
    _, ref = _provision(rt, image)
    req = _request(ref, image)
    out = ev.evaluate(req)
    assert out.error is None, out.error
    assert out.results == {"page-greeting": False, "page-still-served": True}
    assert out.snapshot_digest and out.snapshot_digest.startswith("sha256:")
    assert _leftovers(rt, req.submission_id) == []


def test_edited_workspace_passes_and_runs_on_isolated_copy(env: tuple[Any, Any, str]) -> None:
    rt, ev, image = env
    box, ref = _provision(rt, image)
    code = (
        "import pathlib; p = pathlib.Path('/workspace/index.html');"
        "p.write_text(p.read_text().replace('</h1>', '</h1><p>Olá, CECyber</p>'))"
    )
    assert box.exec_run(["python", "-c", code], user="10001").exit_code == 0
    # Link simbólico para fora do workspace não deve chegar à cópia avaliada.
    assert box.exec_run(["ln", "-s", "/etc/passwd", "/workspace/leak"], user="10001").exit_code == 0
    req = _request(ref, image)
    out = ev.evaluate(req)
    assert out.error is None, out.error
    assert out.results == {"page-greeting": True, "page-still-served": True}
    assert _leftovers(rt, req.submission_id) == []
    # O contêiner da sessão não foi alterado pela avaliação.
    assert box.exec_run(["cat", "/workspace/index.html"]).output.decode().count("Olá, CECyber") == 1


def test_app_that_never_starts_fails_criteria_without_error_leak(env: tuple[Any, Any, str]) -> None:
    rt, ev, image = env
    _, ref = _provision(rt, image)
    req = replace(_request(ref, image), startup_command=("python", "-c", "import sys; sys.exit(1)"))
    req = replace(req, timeout_seconds=40)
    out = ev.evaluate(req)
    assert out.error is None and not any(out.results.values())
    assert _leftovers(rt, req.submission_id) == []


def test_foreign_or_missing_runtime_is_technical_error(env: tuple[Any, Any, str]) -> None:
    _, ev, image = env
    out = ev.evaluate(_request("cecyber-does-not-exist", image))
    assert out.error and not out.results
