"""Apoio comum aos testes de validação de laboratórios contra Docker real (ADR-010/ADR-015)."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime
from typing import Any

import yaml
from app.runtime.port import ProvisionRequest, ResourceLimits, RuntimePhase
from app.validation.port import EvaluationOutcome, EvaluationRequest
from app.validation.suites import HttpSuite, get_suite

from tests.docker_support import LABS


class LabUnderTest:
    """Lê o manifesto do laboratório e executa provisionamento e avaliação como o worker faria."""

    def __init__(self, lab_dir: str, image: str) -> None:
        manifest = yaml.safe_load((LABS / lab_dir / "manifest.yaml").read_text(encoding="utf-8"))
        variant = manifest["variants"][0]
        self.release = f"{manifest['metadata']['id']}@{manifest['metadata']['version']}"
        self.variant_id = variant["id"]
        self.command = tuple(variant["startup"]["command"])
        self.port = int(variant["startup"]["port"])
        res = variant["resources"]
        self.resources = ResourceLimits(
            res["cpuMillicores"], res["memoryMiB"], res["storageMiB"], res["pidsMax"]
        )
        self.image = image
        self.http_ref = next(
            s["validatorRef"]
            for s in manifest["steps"]
            if isinstance(get_suite(s["validatorRef"]), HttpSuite)
        )

    def provision(self, rt: Any) -> tuple[Any, str]:
        ref = rt.provision(
            ProvisionRequest(
                session_id=str(uuid.uuid4()),
                lab_release=self.release,
                variant_id=self.variant_id,
                image_digest=self.image,
                runtime_profile="web-basic",
                resources=self.resources,
                egress_profile="deny-all",
                exposed_port=self.port,
                expires_at=datetime(2030, 1, 1, tzinfo=UTC),
                startup_command=self.command,
                workspace_path="/workspace",
            )
        )
        deadline = time.monotonic() + 120
        while rt.inspect(ref).phase is RuntimePhase.PENDING and time.monotonic() < deadline:
            time.sleep(0.5)
        assert rt.inspect(ref).phase is RuntimePhase.READY
        return rt._client.containers.get(ref), ref

    def outcome(self, ev: Any, ref: str) -> EvaluationOutcome:
        suite = get_suite(self.http_ref)
        assert isinstance(suite, HttpSuite)
        req = EvaluationRequest(
            submission_id=str(uuid.uuid4()),
            runtime_ref=ref,
            image_digest=self.image,
            workspace_path="/workspace",
            startup_command=self.command,
            app_port=self.port,
            checks=suite.probe_checks(),
            logins=suite.probe_logins(),
            cpu_millicores=self.resources.cpu_millicores,
            memory_mib=self.resources.memory_mib,
            pids_max=self.resources.pids_max,
            timeout_seconds=suite.timeout_seconds,
        )
        out: EvaluationOutcome = ev.evaluate(req)
        assert out.error is None, out.error
        return out

    def evaluate(self, ev: Any, ref: str) -> dict[str, bool]:
        out = self.outcome(ev, ref)
        assert out.app_started, out.app_log_tail
        return out.results


def replace_in_file(box: Any, path: str, old: str, new: str) -> None:
    code = (
        "import pathlib,sys; p=pathlib.Path(sys.argv[1]); s=p.read_text(encoding='utf-8');"
        "assert sys.argv[2] in s, 'trecho original não encontrado';"
        "p.write_text(s.replace(sys.argv[2], sys.argv[3]), encoding='utf-8')"
    )
    res = box.exec_run(["python", "-c", code, path, old, new], user="10001")
    assert res.exit_code == 0, res.output
