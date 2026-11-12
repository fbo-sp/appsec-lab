"""Port de avaliação comportamental (ADR-010): snapshot do workspace + execução isolada + probe."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class EvaluationRequest:
    submission_id: str
    runtime_ref: str
    image_digest: str
    workspace_path: str
    startup_command: tuple[str, ...]
    app_port: int
    checks: list[dict[str, Any]]
    cpu_millicores: int
    memory_mib: int
    pids_max: int
    timeout_seconds: int


@dataclass(frozen=True, slots=True)
class EvaluationOutcome:
    snapshot_digest: str | None
    results: dict[str, bool] = field(default_factory=dict)
    error: str | None = None  # falha técnica => ERROR (nunca aprovação)


class EvaluationError(Exception):
    """Falha técnica da avaliação (timeout, runtime indisponível). Não reprova nem aprova o aluno."""


class EvaluatorPort(Protocol):
    def evaluate(self, request: EvaluationRequest) -> EvaluationOutcome: ...


class FakeEvaluator:
    """Para testes: resultados programáveis por id de verificação (padrão: tudo passa)."""

    def __init__(self) -> None:
        self.results: dict[str, bool] = {}
        self.error: str | None = None
        self.calls: list[EvaluationRequest] = []

    def evaluate(self, request: EvaluationRequest) -> EvaluationOutcome:
        self.calls.append(request)
        if self.error:
            return EvaluationOutcome(None, {}, self.error)
        res = {c["id"]: self.results.get(c["id"], True) for c in request.checks}
        return EvaluationOutcome("sha256:" + "0" * 64, res)
