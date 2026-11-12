from __future__ import annotations

from app.config import Settings
from app.runtime.fake import FakeRuntimeAdapter
from app.runtime.port import RuntimePort


def build_runtime(settings: Settings) -> RuntimePort:
    if settings.runtime_adapter == "fake":
        return FakeRuntimeAdapter()
    if settings.runtime_adapter == "docker":
        # Import tardio: o SDK Docker é dependência opcional (extra "docker-runtime").
        from app.runtime.docker_local import DockerRuntimeAdapter

        return DockerRuntimeAdapter(
            attach_container=settings.docker_attach_container, allow_pull=settings.docker_allow_pull
        )
    raise ValueError(f"adapter não suportado: {settings.runtime_adapter}")  # bloqueado por Settings.check
