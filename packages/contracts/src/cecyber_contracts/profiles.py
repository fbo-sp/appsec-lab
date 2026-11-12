"""Perfis de runtime aprovados pela plataforma (docs/09_PROVISIONING_SPEC.md §7).

O manifesto apenas *referencia* um perfil; tetos de recursos e TTL são política
server-side. Um manifesto não pode pedir mais do que o perfil permite.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeProfile:
    name: str
    max_cpu_millicores: int
    max_memory_mib: int
    max_storage_mib: int
    max_pids: int
    max_ttl_minutes: int
    enabled: bool
    disabled_reason: str | None = None


DEFAULT_RUNTIME_PROFILES: dict[str, RuntimeProfile] = {
    p.name: p
    for p in (
        # Perfil para laboratórios benignos de teste do motor (sem vulnerabilidade).
        RuntimeProfile("benign-test", 250, 256, 256, 64, 60, enabled=True),
        RuntimeProfile("web-basic", 500, 512, 1024, 128, 90, enabled=True),
        RuntimeProfile("api-basic", 500, 512, 1024, 128, 90, enabled=True),
        # LAB-004 depende de isolamento reforçado aprovado (ADR-002, PRV-06).
        RuntimeProfile(
            "exec-restricted",
            500,
            512,
            1024,
            64,
            60,
            enabled=False,
            disabled_reason="Aguardando aprovação de isolamento reforçado (ADR-002 / PRV-06).",
        ),
    )
}
