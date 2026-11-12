"""Port de runtime consolidado (G-06 de docs/22): contrato único para adapters fake e reais.

Semântica obrigatória para qualquer adapter (verificada pela suíte de contrato):
- ``provision`` é idempotente por ``session_id`` e usa nomes determinísticos;
  pedir novamente com a MESMA política retorna o mesmo ``runtime_ref``;
  com política divergente lança ``RuntimeConflictError`` (não reutiliza);
- ``inspect`` só observa; ref desconhecido => fase ``ABSENT``;
- ``terminate`` é idempotente; terminar algo ausente não é erro;
- ``list_owned`` lista apenas recursos criados pela plataforma (para reconciliação).
O adapter nunca recebe dados vindos diretamente do navegador.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class RuntimePhase(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    FAILED = "FAILED"
    TERMINATING = "TERMINATING"
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    cpu_millicores: int
    memory_mib: int
    storage_mib: int
    pids_max: int


@dataclass(frozen=True, slots=True)
class ProvisionRequest:
    """Contrato de docs/09 §2, resolvido server-side a partir da release aprovada."""

    session_id: str
    lab_release: str  # "LAB-000@0.1.0"
    variant_id: str
    image_digest: str
    runtime_profile: str
    resources: ResourceLimits
    egress_profile: str
    exposed_port: int
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class RuntimeStatus:
    runtime_ref: str
    phase: RuntimePhase
    reason: str | None = None  # motivo sanitizado, sem detalhes internos


@dataclass(frozen=True, slots=True)
class OwnedRuntime:
    runtime_ref: str
    session_id: str


class RuntimeAdapterError(Exception):
    """Base dos erros do adapter."""


class RuntimeTransientError(RuntimeAdapterError):
    """Falha recuperável (orquestrador indisponível, timeout): o worker tenta novamente."""


class RuntimePermanentError(RuntimeAdapterError):
    """Falha não recuperável (política/imagem rejeitada): sessão vai a FAILED."""


class RuntimeConflictError(RuntimePermanentError):
    """Recurso existente para a sessão diverge da política solicitada."""


class RuntimePort(Protocol):
    provider: str

    def provision(self, request: ProvisionRequest) -> str: ...

    def inspect(self, runtime_ref: str) -> RuntimeStatus: ...

    def reset(self, runtime_ref: str, revision: int) -> None: ...

    def terminate(self, runtime_ref: str) -> None: ...

    def list_owned(self) -> list[OwnedRuntime]: ...

    def ref_for(self, session_id: str) -> str: ...
