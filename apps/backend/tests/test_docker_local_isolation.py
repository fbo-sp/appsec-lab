"""Controles do DockerRuntimeAdapter LOCAL (ADR-008), verificados contra o Docker real.

Estes testes comprovam os controles mínimos declarados no ADR-008; NÃO comprovam isolamento adequado
para código hostil (isso continua dependendo da PoC de ADR-001/002, SEC-02-14).
"""

from __future__ import annotations

import io
import time
import uuid
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

import pytest
from app.runtime.port import (
    ProvisionRequest,
    ResourceLimits,
    RuntimePermanentError,
    RuntimePhase,
)

from tests.docker_support import LAB000_RUNTIME, docker_lab_image


@pytest.fixture
def rt() -> Iterator[Any]:
    image = docker_lab_image()
    from app.runtime.docker_local import DockerRuntimeAdapter

    adapter = DockerRuntimeAdapter()
    adapter.test_image = image  # type: ignore[attr-defined]
    try:
        yield adapter
    finally:
        for owned in adapter.list_owned():
            adapter.terminate(owned.runtime_ref)


def _req(image: str, sid: str | None = None) -> ProvisionRequest:
    return ProvisionRequest(
        session_id=sid or str(uuid.uuid4()),
        lab_release="LAB-000@0.2.0",
        variant_id="python-http",
        image_digest=image,
        runtime_profile="benign-test",
        resources=ResourceLimits(100, 128, 64, 32),
        egress_profile="deny-all",
        exposed_port=8080,
        expires_at=datetime(2030, 1, 1, tzinfo=UTC),
        startup_command=("python", "-m", "http.server", "8080", "--bind", "0.0.0.0"),
        workspace_path="/workspace",
    )


def _ready(rt: Any, ref: str) -> None:
    deadline = time.monotonic() + 60
    while rt.inspect(ref).phase is RuntimePhase.PENDING and time.monotonic() < deadline:
        time.sleep(0.5)
    assert rt.inspect(ref).phase is RuntimePhase.READY


def _py(container: Any, code: str) -> int:
    exit_code, _ = container.exec_run(["python", "-c", code])
    return int(exit_code)


def test_container_hardening_matches_adr_008(rt: Any) -> None:
    ref = rt.provision(_req(rt.test_image))
    _ready(rt, ref)
    c = rt._client.containers.get(ref)
    host = c.attrs["HostConfig"]
    assert c.attrs["Config"]["User"] == "10001"
    assert host["ReadonlyRootfs"] is True
    assert host["CapDrop"] == ["ALL"]
    assert "no-new-privileges:true" in host["SecurityOpt"]
    assert host["Privileged"] is False
    assert host["PidsLimit"] == 32
    assert host["Memory"] == 128 * 1024 * 1024
    assert host["MemorySwap"] == host["Memory"]
    assert host["NanoCpus"] == 100_000_000
    assert not host.get("PortBindings")  # nada publicado no host
    binds = [m["Source"] for m in c.attrs["Mounts"] if m["Type"] == "bind"]
    assert binds == []  # sem montagens do host (incl. socket Docker)
    env = c.attrs["Config"]["Env"] or []
    assert not any(e.startswith(("DATABASE_URL", "DOCKER_", "POSTGRES")) for e in env)
    nets = c.attrs["NetworkSettings"]["Networks"]
    assert list(nets) == [f"{ref}-net"]
    assert rt._client.networks.get(f"{ref}-net").attrs["Internal"] is True


def test_no_egress_and_no_cross_session_reachability(rt: Any) -> None:
    a = rt.provision(_req(rt.test_image))
    b = rt.provision(_req(rt.test_image))
    _ready(rt, a)
    _ready(rt, b)
    ca = rt._client.containers.get(a)
    ep_a, ep_b = rt.endpoint(a), rt.endpoint(b)
    assert ep_a is not None and ep_b is not None and ep_a.port == 8080
    # A aplicação responde dentro da própria sessão…
    assert _py(ca, "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=3)") == 0
    # …mas não alcança a sessão vizinha nem a Internet.
    probe = "import socket; s=socket.create_connection(({!r}, {}), timeout=3)"
    assert _py(ca, probe.format(ep_b.host, ep_b.port)) != 0
    assert _py(ca, probe.format("1.1.1.1", 443)) != 0
    assert _py(ca, "import socket; socket.getaddrinfo('example.com', 443)") != 0


def test_workspace_is_writable_but_root_fs_is_not(rt: Any) -> None:
    ref = rt.provision(_req(rt.test_image))
    _ready(rt, ref)
    c = rt._client.containers.get(ref)
    assert _py(c, "open('/workspace/novo.txt','w').write('ok')") == 0
    assert _py(c, "import os; assert os.path.exists('/workspace/index.html')") == 0
    assert _py(c, "open('/etc/x','w')") != 0
    assert _py(c, "open('/tmp/t','w').write('ok')") == 0


def test_root_image_is_rejected(rt: Any) -> None:
    client = rt._client
    df = f"FROM {rt.test_image.rsplit('@', 1)[1]}\nUSER 0\n"
    image, _ = client.images.build(fileobj=io.BytesIO(df.encode()), tag="cecyber-labs/root:local", rm=True)
    try:
        with pytest.raises(RuntimePermanentError, match="não-root"):
            rt.provision(replace(_req(rt.test_image), image_digest=f"local/x@{image.id}"))
    finally:
        client.images.remove(image.id, force=True)


def test_unknown_image_is_permanent_and_pull_is_disabled(rt: Any) -> None:
    with pytest.raises(RuntimePermanentError):
        rt.provision(replace(_req(rt.test_image), image_digest="docker.io/library/x@sha256:" + "cd" * 32))


def test_foreign_container_with_same_name_is_never_touched(rt: Any) -> None:
    sid = str(uuid.uuid4())
    ref = rt.ref_for(sid)
    foreign = rt._client.containers.create(rt.test_image.rsplit("@", 1)[1], name=ref, command=["true"])
    try:
        with pytest.raises(RuntimePermanentError):
            rt.provision(_req(rt.test_image, sid))
        assert rt._client.containers.get(ref).id == foreign.id
    finally:
        foreign.remove(force=True)


def test_runtime_source_has_lab_dockerfile() -> None:
    assert (LAB000_RUNTIME / "Dockerfile").is_file()
