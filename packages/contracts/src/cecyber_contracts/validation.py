"""Validação estrutural + semântica do manifesto (docs/11_LAB_MANIFEST_SPEC.md §3).

``validate_manifest`` devolve o modelo validado ou lança ``ManifestValidationError``
com uma lista de problemas localizados (``loc``), adequada a feedback de autor.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from cecyber_contracts.manifest import AppSecLab
from cecyber_contracts.profiles import DEFAULT_RUNTIME_PROFILES, RuntimeProfile

REQUIRED_TOTAL_POINTS = 100
_FORBIDDEN_DIGESTS = {"0" * 64, "f" * 64}


@dataclass(frozen=True, slots=True)
class ManifestIssue:
    loc: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"loc": self.loc, "code": self.code, "message": self.message}


class ManifestValidationError(Exception):
    def __init__(self, issues: list[ManifestIssue]) -> None:
        self.issues = issues
        super().__init__("; ".join(f"{i.loc}: {i.message}" for i in issues))


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Carrega YAML com ``safe_load`` (sem tags/objetos arbitrários)."""
    with Path(path).open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ManifestValidationError([ManifestIssue("$", "NOT_A_MAPPING", "Manifesto deve ser um objeto.")])
    return data


def _structural(data: Mapping[str, Any]) -> AppSecLab:
    try:
        return AppSecLab.model_validate(data)
    except ValidationError as exc:
        issues = [
            ManifestIssue(
                loc=".".join(str(p) for p in err["loc"]) or "$",
                code=str(err["type"]).upper(),
                message=str(err["msg"]),
            )
            for err in exc.errors()
        ]
        raise ManifestValidationError(issues) from exc


def _duplicates(values: list[Any]) -> set[Any]:
    return {v for v, n in Counter(values).items() if n > 1}


def _semantic(m: AppSecLab, profiles: Mapping[str, RuntimeProfile]) -> list[ManifestIssue]:
    issues: list[ManifestIssue] = []
    add = issues.append

    if m.metadata.primary_cwe in m.metadata.secondary_cwes:
        add(
            ManifestIssue(
                "metadata.secondaryCwes", "DUPLICATE_CWE", "CWE principal repetida nas secundárias."
            )
        )

    # Variantes
    for dup in _duplicates([v.id for v in m.variants]):
        add(ManifestIssue("variants", "DUPLICATE_VARIANT_ID", f"Variante duplicada: {dup}"))
    for i, v in enumerate(m.variants):
        loc = f"variants.{i}"
        digest = v.image.rsplit("@sha256:", 1)[1]
        if digest in _FORBIDDEN_DIGESTS:
            add(ManifestIssue(f"{loc}.image", "PLACEHOLDER_DIGEST", "Digest de imagem é um placeholder."))
        if len(set(v.interfaces)) != len(v.interfaces):
            add(ManifestIssue(f"{loc}.interfaces", "DUPLICATE_INTERFACE", "Interface repetida."))
        profile = profiles.get(v.runtime_profile)
        if profile is None:
            add(
                ManifestIssue(
                    f"{loc}.runtimeProfile", "UNKNOWN_PROFILE", f"Perfil desconhecido: {v.runtime_profile}"
                )
            )
            continue
        if not profile.enabled:
            add(
                ManifestIssue(
                    f"{loc}.runtimeProfile",
                    "PROFILE_DISABLED",
                    profile.disabled_reason or "Perfil desabilitado.",
                )
            )
        r = v.resources
        limits = (
            ("cpuMillicores", r.cpu_millicores, profile.max_cpu_millicores),
            ("memoryMiB", r.memory_mib, profile.max_memory_mib),
            ("storageMiB", r.storage_mib, profile.max_storage_mib),
            ("pidsMax", r.pids_max, profile.max_pids),
        )
        for field, value, ceiling in limits:
            if value > ceiling:
                add(
                    ManifestIssue(
                        f"{loc}.resources.{field}",
                        "EXCEEDS_PROFILE",
                        f"{value} excede o teto {ceiling} do perfil {profile.name}.",
                    )
                )
        if v.session.ttl_minutes > profile.max_ttl_minutes:
            add(
                ManifestIssue(
                    f"{loc}.session.ttlMinutes",
                    "EXCEEDS_PROFILE",
                    f"TTL excede {profile.max_ttl_minutes} min do perfil {profile.name}.",
                )
            )

    # Etapas
    for dup in _duplicates([s.id for s in m.steps]):
        add(ManifestIssue("steps", "DUPLICATE_STEP_ID", f"Etapa duplicada: {dup}"))
    orders = sorted(s.order for s in m.steps)
    if orders != list(range(1, len(m.steps) + 1)):
        add(
            ManifestIssue(
                "steps",
                "NON_CONTIGUOUS_ORDER",
                "Ordens das etapas devem ser únicas e contíguas a partir de 1.",
            )
        )
    for i, s in enumerate(m.steps):
        levels = sorted(h.level for h in s.hints)
        if levels != list(range(1, len(s.hints) + 1)):
            add(
                ManifestIssue(
                    f"steps.{i}.hints",
                    "INVALID_HINT_LEVELS",
                    "Níveis de dica devem ser únicos e contíguos a partir de 1.",
                )
            )
    total = sum(s.points for s in m.steps)
    if total != REQUIRED_TOTAL_POINTS:
        add(
            ManifestIssue(
                "steps",
                "INVALID_TOTAL_POINTS",
                f"Soma de pontos das etapas deve ser {REQUIRED_TOTAL_POINTS} (atual: {total}).",
            )
        )
    if m.policy.final_passing_score > total:
        add(
            ManifestIssue(
                "policy.finalPassingScore",
                "UNREACHABLE_PASSING_SCORE",
                "Nota mínima maior que a pontuação total.",
            )
        )
    return issues


def validate_manifest(
    data: Mapping[str, Any],
    profiles: Mapping[str, RuntimeProfile] = DEFAULT_RUNTIME_PROFILES,
) -> AppSecLab:
    manifest = _structural(data)
    issues = _semantic(manifest, profiles)
    if issues:
        raise ManifestValidationError(issues)
    return manifest
