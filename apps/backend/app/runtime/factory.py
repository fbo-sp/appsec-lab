from __future__ import annotations

from app.config import Settings
from app.runtime.fake import FakeRuntimeAdapter
from app.runtime.port import RuntimePort


def build_runtime(settings: Settings) -> RuntimePort:
    if settings.runtime_adapter == "fake":
        return FakeRuntimeAdapter()
    raise ValueError(f"adapter não suportado: {settings.runtime_adapter}")  # bloqueado por Settings.check
