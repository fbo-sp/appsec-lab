"""FakeRuntimeAdapter: implementação em memória do RuntimePort para testes e desenvolvimento.

NÃO executa contêineres, NÃO faz pull de imagens e NÃO oferece isolamento. Serve para provar
o contrato do motor (NFR-015, ENG-08) com recursos benignos. Suporta injeção de falhas.
Estado é por processo: com múltiplos workers em processos distintos o fake não é compartilhado.
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field

from app.runtime.port import (
    OwnedRuntime,
    ProvisionRequest,
    RuntimeConflictError,
    RuntimePermanentError,
    RuntimePhase,
    RuntimeStatus,
    RuntimeTransientError,
)


@dataclass
class _Instance:
    request: ProvisionRequest
    phase: RuntimePhase
    revision: int = 0
    pending_polls: int = 0


@dataclass
class FaultPlan:
    """Falhas programadas, consumidas em ordem: 'transient' | 'permanent' | None."""

    provision: deque[str | None] = field(default_factory=deque)
    terminate: deque[str | None] = field(default_factory=deque)
    # número de chamadas a inspect que retornam PENDING antes de READY
    ready_after_polls: int = 0
    # se True, o runtime nunca fica pronto (simula timeout de readiness)
    never_ready: bool = False


class FakeRuntimeAdapter:
    provider = "fake"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._instances: dict[str, _Instance] = {}
        self.faults = FaultPlan()
        self.calls: list[tuple[str, str]] = []

    @staticmethod
    def ref_for(session_id: str) -> str:
        return f"fake-{session_id}"

    @staticmethod
    def _raise(kind: str | None, op: str) -> None:
        if kind == "transient":
            raise RuntimeTransientError(f"falha transitória injetada em {op}")
        if kind == "permanent":
            raise RuntimePermanentError(f"falha permanente injetada em {op}")

    def provision(self, request: ProvisionRequest) -> str:
        with self._lock:
            self.calls.append(("provision", request.session_id))
            if self.faults.provision:
                self._raise(self.faults.provision.popleft(), "provision")
            ref = self.ref_for(request.session_id)
            existing = self._instances.get(ref)
            if existing is not None:
                if existing.request != request:
                    raise RuntimeConflictError("instância existente diverge da política solicitada")
                return ref
            self._instances[ref] = _Instance(
                request=request,
                phase=RuntimePhase.PENDING,
                pending_polls=self.faults.ready_after_polls,
            )
            return ref

    def inspect(self, runtime_ref: str) -> RuntimeStatus:
        with self._lock:
            inst = self._instances.get(runtime_ref)
            if inst is None:
                return RuntimeStatus(runtime_ref, RuntimePhase.ABSENT)
            if inst.phase is RuntimePhase.PENDING and not self.faults.never_ready:
                if inst.pending_polls > 0:
                    inst.pending_polls -= 1
                else:
                    inst.phase = RuntimePhase.READY
            return RuntimeStatus(runtime_ref, inst.phase)

    def reset(self, runtime_ref: str, revision: int) -> None:
        with self._lock:
            inst = self._instances.get(runtime_ref)
            if inst is None:
                raise RuntimePermanentError("runtime ausente")
            inst.revision = revision

    def terminate(self, runtime_ref: str) -> None:
        with self._lock:
            self.calls.append(("terminate", runtime_ref))
            if self.faults.terminate:
                self._raise(self.faults.terminate.popleft(), "terminate")
            self._instances.pop(runtime_ref, None)

    def list_owned(self) -> list[OwnedRuntime]:
        with self._lock:
            return [OwnedRuntime(ref, inst.request.session_id) for ref, inst in self._instances.items()]

    # Utilitário de teste: cria um runtime sem sessão correspondente (órfão).
    def inject_orphan(self, request: ProvisionRequest) -> str:
        with self._lock:
            ref = self.ref_for(request.session_id)
            self._instances[ref] = _Instance(request=request, phase=RuntimePhase.READY)
            return ref
