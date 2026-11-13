"""Avaliador Docker LOCAL (ADR-010). Executado pelo worker (plano de controle), nunca pelo aluno.

1. Snapshot: copia o workspace do contêiner da sessão (``get_archive``) e calcula o digest. Edições
   posteriores do aluno não afetam a avaliação.
2. Cópia isolada: cria um contêiner NOVO da mesma imagem, com o snapshot num volume próprio, em rede
   ``internal`` exclusiva da avaliação, com o mesmo endurecimento do runtime (ADR-008).
3. Probe confiável: contêiner efêmero (sem segredos, sem socket) que executa as verificações da suíte
   protegida contra a cópia e devolve um JSON; nada roda dentro do workspace editável.
4. Limpeza garantida de contêineres, rede e volume da avaliação.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import tarfile
import time
from importlib import resources
from typing import Any

import docker
from docker.errors import DockerException, NotFound
from docker.types import Mount

from app.runtime.docker_local import EVAL_LABEL, PLATFORM_LABEL, PLATFORM_VALUE
from app.validation.port import EvaluationOutcome, EvaluationRequest

MAX_SNAPSHOT = 20 * 1024 * 1024
LOG_TAIL_LINES = 15
LOG_TAIL_CHARS = 2000


def _strip_top_dir(raw: bytes) -> bytes:
    """``get_archive`` devolve ``workspace/...``; reempacota relativo para extrair no próprio volume."""
    out = io.BytesIO()
    with tarfile.open(fileobj=io.BytesIO(raw)) as src, tarfile.open(fileobj=out, mode="w") as dst:
        for m in src.getmembers():
            parts = m.name.split("/", 1)
            if len(parts) < 2 or not parts[1]:
                continue
            if m.issym() or m.islnk() or m.isdev() or m.name.startswith("/") or ".." in parts[1].split("/"):
                continue  # links, dispositivos e caminhos fora do workspace não vão para a cópia avaliada
            m.name = parts[1]
            dst.addfile(m, src.extractfile(m) if m.isfile() else None)
    return out.getvalue()


def _tar(files: dict[str, bytes]) -> bytes:
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w") as t:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o444
            t.addfile(info, io.BytesIO(data))
    return out.getvalue()


class DockerEvaluator:
    def __init__(
        self, client: Any | None = None, *, probe_image: str = "cecyber-labs/base-python:local"
    ) -> None:
        self._client = client or docker.from_env()
        self._probe_image = probe_image

    def evaluate(self, request: EvaluationRequest) -> EvaluationOutcome:
        name = f"cecyber-eval-{request.submission_id}"
        labels = {PLATFORM_LABEL: PLATFORM_VALUE, EVAL_LABEL: request.submission_id}
        created: list[Any] = []
        net = vol = None
        digest: str | None = None
        try:
            src = self._client.containers.get(request.runtime_ref)
            if src.labels.get(PLATFORM_LABEL) != PLATFORM_VALUE:
                return EvaluationOutcome(None, {}, "runtime alheio à plataforma")
            stream, _ = src.get_archive(request.workspace_path)
            raw = b""
            for chunk in stream:
                raw += chunk
                if len(raw) > MAX_SNAPSHOT:
                    return EvaluationOutcome(None, {}, "workspace excede o limite de snapshot")
            digest = "sha256:" + hashlib.sha256(raw).hexdigest()
            snapshot = _strip_top_dir(raw)

            net = self._client.networks.create(
                f"{name}-net",
                driver="bridge",
                internal=True,
                labels=labels,
                options={"com.docker.network.bridge.enable_ip_masquerade": "false"},
            )
            vol = self._client.volumes.create(f"{name}-ws", labels=labels)
            image_id = "sha256:" + request.image_digest.rsplit("@sha256:", 1)[1]
            app = self._client.containers.create(
                image_id,
                # Só a aplicação: o agente de workspace (terminal/arquivos) NÃO roda na cópia avaliada.
                entrypoint=list(request.startup_command),
                command=[],
                name=name,
                labels=labels,
                network=net.name,
                working_dir=request.workspace_path,
                mounts=[Mount(request.workspace_path, vol.name, type="volume", no_copy=True)],
                read_only=True,
                tmpfs={"/tmp": "rw,noexec,nosuid,nodev,size=64m"},  # noqa: S108 - tmpfs do contêiner
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                pids_limit=request.pids_max,
                mem_limit=f"{request.memory_mib}m",
                memswap_limit=f"{request.memory_mib}m",
                nano_cpus=request.cpu_millicores * 1_000_000,
                environment={},
            )
            created.append(app)
            app.put_archive(request.workspace_path, snapshot)
            app.start()

            spec = {
                "base": f"http://{name}:{request.app_port}",
                "checks": request.checks,
                "wait_seconds": min(30, request.timeout_seconds),
            }
            probe_src = resources.files("app.validation").joinpath("probe.py").read_bytes()
            # Probe: código confiável (suíte + script) copiado antes do start; raiz gravável apenas para
            # receber esses arquivos (contêiner efêmero, sem segredos, sem socket, sem portas).
            probe = self._client.containers.create(
                self._probe_image,
                entrypoint=["python", "/probe/probe.py", "/probe/spec.json"],
                command=[],
                name=f"{name}-probe",
                labels=labels,
                network=net.name,
                user="10001",
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                pids_limit=32,
                mem_limit="128m",
                environment={},
            )
            created.append(probe)
            probe.put_archive(
                "/", _tar({"probe/probe.py": probe_src, "probe/spec.json": json.dumps(spec).encode()})
            )
            probe.start()
            status = probe.wait(timeout=request.timeout_seconds)
            out = probe.logs(stdout=True, stderr=False).decode("utf-8", "replace").strip().splitlines()
            if status.get("StatusCode") != 0 or not out:
                return EvaluationOutcome(digest, {}, "probe de validação falhou")
            parsed = json.loads(out[-1])
            if parsed.get("started") is False:
                tail = app.logs(stdout=True, stderr=True, tail=LOG_TAIL_LINES).decode("utf-8", "replace")
                return EvaluationOutcome(digest, {}, app_started=False, app_log_tail=tail[-LOG_TAIL_CHARS:])
            results = {str(k): bool(v) for k, v in parsed.get("results", {}).items()}
            return EvaluationOutcome(digest, results)
        except (DockerException, ValueError, KeyError, tarfile.TarError) as exc:
            return EvaluationOutcome(digest, {}, f"falha técnica na avaliação: {type(exc).__name__}")
        except Exception as exc:  # timeout de wait (requests) e afins: sempre ERROR, nunca aprovação
            return EvaluationOutcome(digest, {}, f"falha técnica na avaliação: {type(exc).__name__}")
        finally:
            for c in created:
                with contextlib.suppress(DockerException):
                    c.remove(force=True)
            for res in (net, vol):
                if res is not None:
                    for _ in range(3):
                        try:
                            res.remove()
                            break
                        except NotFound:
                            break
                        except DockerException:
                            time.sleep(0.5)
