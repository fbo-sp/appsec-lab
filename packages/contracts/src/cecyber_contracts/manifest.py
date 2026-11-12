"""Modelo estrutural do manifesto ``AppSecLab`` v1alpha1 (docs/11_LAB_MANIFEST_SPEC.md).

Decisões de contrato (ADR-006, proposto):
- campos desconhecidos são rejeitados (``extra="forbid"``) em todos os níveis;
- o estado de publicação (draft/published/retired) NÃO pertence ao manifesto;
- comandos são listas de argumentos (nunca string de shell);
- a única política de rede aceita é ``deny-all`` (BR-009, OPEN-09 pendente).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

API_VERSION = "labs.cecyber.io/v1alpha1"
KIND = "AppSecLab"

LabId = Annotated[str, StringConstraints(pattern=r"^LAB-[0-9]{3}$")]
SemVer = Annotated[
    str,
    StringConstraints(pattern=r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"),
]
Cwe = Annotated[str, StringConstraints(pattern=r"^CWE-[1-9][0-9]{0,4}$")]
Slug = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", max_length=63)]
# Referência OCI obrigatoriamente fixada por digest sha256 real (64 hex). Tags são proibidas.
ImageRef = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z0-9]+([._-][a-z0-9]+)*(:[0-9]+)?(/[a-z0-9]+([._-][a-z0-9]+)*)+@sha256:[a-f0-9]{64}$",
        max_length=255,
    ),
]
# validatorRef: <grupo>/<variante>/<nome>-v<N>; resolvido no registro protegido de validadores.
ValidatorRef = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z0-9-]+(/[a-z0-9-]+)+-v[0-9]+$", max_length=200),
]
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
CommandArg = Annotated[str, StringConstraints(min_length=1, max_length=512)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class Difficulty(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Interface(StrEnum):
    EDITOR = "editor"
    TERMINAL = "terminal"
    WEB = "web"


class Metadata(_Strict):
    id: LabId
    version: SemVer
    title: ShortText
    primary_cwe: Cwe = Field(alias="primaryCwe")
    secondary_cwes: tuple[Cwe, ...] = Field(default=(), alias="secondaryCwes", max_length=5)


class Story(_Strict):
    role: NonEmptyText
    application: NonEmptyText
    context: NonEmptyText
    mission: NonEmptyText


class Learning(_Strict):
    single_vulnerability: Literal[True] = Field(alias="singleVulnerability")
    estimated_minutes: int = Field(alias="estimatedMinutes", ge=5, le=240)
    difficulty: Difficulty
    objectives: tuple[NonEmptyText, ...] = Field(min_length=1, max_length=10)
    story: Story


class Startup(_Strict):
    command: tuple[CommandArg, ...] = Field(min_length=1, max_length=32)
    port: int = Field(ge=1024, le=65535)


class Build(_Strict):
    command: tuple[CommandArg, ...] = Field(min_length=1, max_length=32)
    timeout_seconds: int = Field(alias="timeoutSeconds", ge=1, le=300)


class Resources(_Strict):
    cpu_millicores: int = Field(alias="cpuMillicores", ge=50)
    memory_mib: int = Field(alias="memoryMiB", ge=32)
    storage_mib: int = Field(alias="storageMiB", ge=16)
    pids_max: int = Field(default=64, alias="pidsMax", ge=8)


class SessionPolicy(_Strict):
    ttl_minutes: int = Field(alias="ttlMinutes", ge=5)
    # Renovações do prazo pelo aluno (ADR-011): cada uma reinicia o prazo de ``ttlMinutes``.
    max_renewals: int = Field(default=2, alias="maxRenewals", ge=0, le=10)


class Network(_Strict):
    egress_profile: Literal["deny-all"] = Field(default="deny-all", alias="egressProfile")


class LabVariant(_Strict):
    id: Slug
    language: Slug
    framework: Slug
    image: ImageRef
    runtime_profile: Slug = Field(alias="runtimeProfile")
    workspace_path: Annotated[str, StringConstraints(pattern=r"^/workspace(/[A-Za-z0-9._-]+)*$")] = Field(
        alias="workspacePath"
    )
    startup: Startup
    build: Build | None = None
    resources: Resources
    session: SessionPolicy
    network: Network = Network()
    interfaces: tuple[Interface, ...] = Field(min_length=1, max_length=3)


class Hint(_Strict):
    level: int = Field(ge=1, le=3)
    text: NonEmptyText


class LabStep(_Strict):
    id: Slug
    order: int = Field(ge=1, le=50)
    title: ShortText
    explanation: NonEmptyText
    task: NonEmptyText
    concept: NonEmptyText | None = None
    expected_outcome: NonEmptyText | None = Field(default=None, alias="expectedOutcome")
    validator_ref: ValidatorRef = Field(alias="validatorRef")
    hints: tuple[Hint, ...] = Field(default=(), max_length=3)
    unlock_on_pass: bool = Field(default=True, alias="unlockOnPass")
    points: int = Field(ge=0, le=100)


class Policy(_Strict):
    sequential_unlock: bool = Field(alias="sequentialUnlock")
    allow_step_retry: bool = Field(alias="allowStepRetry")
    persist_progress_across_reset: bool = Field(alias="persistProgressAcrossReset")
    allow_solution_reveal: bool = Field(alias="allowSolutionReveal")
    final_passing_score: int = Field(alias="finalPassingScore", ge=0, le=100)


class AppSecLab(_Strict):
    api_version: Literal["labs.cecyber.io/v1alpha1"] = Field(alias="apiVersion")
    kind: Literal["AppSecLab"]
    metadata: Metadata
    learning: Learning
    variants: tuple[LabVariant, ...] = Field(min_length=1, max_length=10)
    steps: tuple[LabStep, ...] = Field(min_length=1, max_length=50)
    policy: Policy
