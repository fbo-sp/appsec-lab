"""DockerRuntimeAdapter — EXCLUSIVO para desenvolvimento/teste local (ADR-008).

Executa o laboratório de uma sessão como contêiner Docker na máquina do desenvolvedor, para permitir
testar a experiência visual antes da PoC de isolamento on-premises (ADR-001/002). NÃO é fronteira de
isolamento aprovada para código hostil e nunca deve ser habilitado fora de APP_ENV=local|test
(``Settings.check`` recusa a configuração).

Controles aplicados a cada contêiner de laboratório:
- rede Docker ``internal`` exclusiva da sessão (sem rota para Internet/host; sem acesso a outras sessões);
- nenhuma porta publicada no host; somente o gateway (se configurado) é conectado à rede da sessão;
- usuário não-root obrigatório (imagem com USER numérico != 0), ``cap_drop=ALL``, ``no-new-privileges``;
- raiz somente leitura, ``/tmp`` em tmpfs ``noexec``; workspace em volume próprio da sessão;
- limites de CPU, memória (sem swap extra) e PIDs vindos da release aprovada;
- sem socket Docker, sem variáveis de ambiente do plano de controle, sem montagens do host;
- imagem resolvida pelo digest/ID local; pull desabilitado por padrão.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
from dataclasses import asdict
from typing import Any

import docker
from docker.errors import APIError, DockerException, ImageNotFound, NotFound

from app.runtime.port import (
    OwnedRuntime,
    ProvisionRequest,
    RuntimeConflictError,
    RuntimeEndpoint,
    RuntimePermanentError,
    RuntimePhase,
    RuntimeStatus,
    RuntimeTransientError,
)

PLATFORM_LABEL = "io.cecyber.appsec-labs.platform"
SESSION_LABEL = "io.cecyber.appsec-labs.session-id"
POLICY_LABEL = "io.cecyber.appsec-labs.policy-hash"
PORT_LABEL = "io.cecyber.appsec-labs.app-port"
PLATFORM_VALUE = "appsec-labs-local"


def _policy_hash(request: ProvisionRequest) -> str:
    data = asdict(request)
    data["expires_at"] = request.expires_at.isoformat()
    raw = json.dumps(data, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()


class DockerRuntimeAdapter:
    provider = "docker-local"

    def __init__(
        self,
        client: Any | None = None,
        *,
        attach_container: str | None = None,
        allow_pull: bool = False,
        tmp_size_mib: int = 64,
    ) -> None:
        try:
            self._client = client or docker.from_env()
        except DockerException as exc:
            raise RuntimeTransientError(f"Docker indisponível: {exc}") from exc
        self._attach = attach_container
        self._allow_pull = allow_pull
        self._tmp_size = tmp_size_mib

    # -- nomes determinísticos ------------------------------------------------------------------
    @staticmethod
    def ref_for(session_id: str) -> str:
        return f"cecyber-lab-{session_id}"

    @staticmethod
    def _network(ref: str) -> str:
        return f"{ref}-net"

    @staticmethod
    def _volume(ref: str) -> str:
        return f"{ref}-ws"

    def _labels(self, request: ProvisionRequest) -> dict[str, str]:
        return {
            PLATFORM_LABEL: PLATFORM_VALUE,
            SESSION_LABEL: request.session_id,
            POLICY_LABEL: _policy_hash(request),
            PORT_LABEL: str(request.exposed_port),
        }

    # -- operações do port ----------------------------------------------------------------------
    def provision(self, request: ProvisionRequest) -> str:
        ref = self.ref_for(request.session_id)
        labels = self._labels(request)
        try:
            existing = self._get(ref)
            if existing is not None:
                if existing.labels.get(POLICY_LABEL) != labels[POLICY_LABEL]:
                    raise RuntimeConflictError("contêiner existente diverge da política solicitada")
                self._ensure_attached(ref)
                return ref
            image = self._resolve_image(request.image_digest)
            self._require_non_root(image)
            net = self._ensure_network(ref, labels)
            self._ensure_volume(ref, labels)
            self._client.containers.run(
                image.id,
                command=list(request.startup_command) or None,
                name=ref,
                hostname=ref[:63],
                labels=labels,
                detach=True,
                network=net.name,
                working_dir=request.workspace_path,
                volumes={self._volume(ref): {"bind": request.workspace_path, "mode": "rw"}},
                read_only=True,
                # tmpfs dentro do contêiner (não é diretório do host).
                tmpfs={"/tmp": f"rw,noexec,nosuid,nodev,size={self._tmp_size}m"},  # noqa: S108
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                privileged=False,
                pids_limit=request.resources.pids_max,
                mem_limit=f"{request.resources.memory_mib}m",
                memswap_limit=f"{request.resources.memory_mib}m",
                nano_cpus=request.resources.cpu_millicores * 1_000_000,
                environment={},
                restart_policy={"Name": "no"},
            )
            self._ensure_attached(ref)
            return ref
        except (RuntimeConflictError, RuntimePermanentError):
            raise
        except ImageNotFound as exc:
            raise RuntimePermanentError("imagem do laboratório não encontrada localmente") from exc
        except APIError as exc:
            if exc.status_code == 409:  # corrida de criação com o mesmo nome: reavaliar idempotente
                return self.provision(request)
            if exc.status_code is not None and 400 <= exc.status_code < 500:
                raise RuntimePermanentError(f"Docker rejeitou a criação: {exc.explanation}") from exc
            raise RuntimeTransientError(f"Docker indisponível: {exc}") from exc
        except DockerException as exc:
            raise RuntimeTransientError(f"Docker indisponível: {exc}") from exc

    def inspect(self, runtime_ref: str) -> RuntimeStatus:
        try:
            c = self._get(runtime_ref)
        except DockerException:
            return RuntimeStatus(runtime_ref, RuntimePhase.UNKNOWN)
        if c is None:
            return RuntimeStatus(runtime_ref, RuntimePhase.ABSENT)
        state = c.attrs.get("State", {})
        status = state.get("Status")
        health = (state.get("Health") or {}).get("Status")
        if status == "running":
            if health in (None, "healthy"):
                return RuntimeStatus(runtime_ref, RuntimePhase.READY)
            if health == "unhealthy":
                return RuntimeStatus(runtime_ref, RuntimePhase.FAILED, "aplicação não saudável")
            return RuntimeStatus(runtime_ref, RuntimePhase.PENDING)
        if status in ("created", "restarting"):
            return RuntimeStatus(runtime_ref, RuntimePhase.PENDING)
        if status == "removing":
            return RuntimeStatus(runtime_ref, RuntimePhase.TERMINATING)
        return RuntimeStatus(runtime_ref, RuntimePhase.FAILED, "aplicação encerrou")

    def reset(self, runtime_ref: str, revision: int) -> None:
        raise RuntimePermanentError("reset ainda não suportado no adapter Docker local (IMP-206)")

    def terminate(self, runtime_ref: str) -> None:
        try:
            c = self._get(runtime_ref)
            if c is not None:
                c.remove(force=True, v=False)
            try:
                net = self._client.networks.get(self._network(runtime_ref))
                if self._attach:
                    with contextlib.suppress(NotFound, APIError):
                        net.disconnect(self._attach, force=True)
                net.remove()
            except NotFound:
                pass
            with contextlib.suppress(NotFound):
                self._client.volumes.get(self._volume(runtime_ref)).remove(force=True)
        except APIError as exc:
            if exc.status_code == 404:
                return
            raise RuntimeTransientError(f"falha ao remover recursos: {exc.explanation}") from exc
        except DockerException as exc:
            raise RuntimeTransientError(f"Docker indisponível: {exc}") from exc

    def list_owned(self) -> list[OwnedRuntime]:
        try:
            flt = {"label": f"{PLATFORM_LABEL}={PLATFORM_VALUE}"}
            found: dict[str, OwnedRuntime] = {}
            for c in self._client.containers.list(all=True, filters=flt):
                found[c.name] = OwnedRuntime(c.name, c.labels.get(SESSION_LABEL, ""))
            # Redes/volumes sem contêiner (criação parcial) também são recursos da plataforma.
            for n in self._client.networks.list(filters=flt):
                ref = n.name.removesuffix("-net")
                found.setdefault(ref, OwnedRuntime(ref, (n.attrs.get("Labels") or {}).get(SESSION_LABEL, "")))
            for v in self._client.volumes.list(filters=flt):
                ref = v.name.removesuffix("-ws")
                found.setdefault(ref, OwnedRuntime(ref, (v.attrs.get("Labels") or {}).get(SESSION_LABEL, "")))
            return list(found.values())
        except DockerException as exc:
            raise RuntimeTransientError(f"Docker indisponível: {exc}") from exc

    def endpoint(self, runtime_ref: str) -> RuntimeEndpoint | None:
        try:
            c = self._get(runtime_ref)
        except DockerException:
            return None
        if c is None:
            return None
        nets = c.attrs.get("NetworkSettings", {}).get("Networks", {})
        info = nets.get(self._network(runtime_ref))
        port = c.labels.get(PORT_LABEL)
        if not info or not info.get("IPAddress") or not port:
            return None
        return RuntimeEndpoint(info["IPAddress"], int(port))

    # -- auxiliares -----------------------------------------------------------------------------
    def _get(self, ref: str) -> Any | None:
        try:
            c = self._client.containers.get(ref)
        except NotFound:
            return None
        if c.labels.get(PLATFORM_LABEL) != PLATFORM_VALUE:
            # Nunca manipular contêineres que não foram criados pela plataforma.
            raise RuntimePermanentError("nome de contêiner em uso por recurso alheio à plataforma")
        return c

    def _resolve_image(self, image_ref: str) -> Any:
        digest = "sha256:" + image_ref.rsplit("@sha256:", 1)[1]
        try:
            return self._client.images.get(digest)  # ID local (build local)
        except ImageNotFound:
            pass
        try:
            return self._client.images.get(image_ref)  # repo digest já presente
        except ImageNotFound:
            if not self._allow_pull:
                raise
            return self._client.images.pull(image_ref)

    @staticmethod
    def _require_non_root(image: Any) -> None:
        user = str(image.attrs.get("Config", {}).get("User") or "").split(":")[0]
        if user in ("", "0", "root"):
            raise RuntimePermanentError("imagem de laboratório deve definir USER não-root")

    def _ensure_network(self, ref: str, labels: dict[str, str]) -> Any:
        name = self._network(ref)
        try:
            return self._client.networks.get(name)
        except NotFound:
            return self._client.networks.create(
                name,
                driver="bridge",
                internal=True,
                labels=labels,
                options={"com.docker.network.bridge.enable_ip_masquerade": "false"},
            )

    def _ensure_volume(self, ref: str, labels: dict[str, str]) -> None:
        try:
            self._client.volumes.get(self._volume(ref))
        except NotFound:
            self._client.volumes.create(self._volume(ref), labels=labels)

    def _ensure_attached(self, ref: str) -> None:
        if not self._attach:
            return
        net = self._client.networks.get(self._network(ref))
        try:
            net.connect(self._attach)
        except APIError as exc:
            if exc.status_code not in (403, 409) and "already exists" not in str(exc):
                raise
