"""Catálogo: registro de releases imutáveis a partir de manifestos validados (FR-010-012)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from cecyber_contracts import (
    AppSecLab,
    ManifestValidationError,
    canonical_manifest_digest,
    validate_manifest,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit import service as audit
from app.db.models import Lab, LabRelease, LabStep, LabVariant, StepHint
from app.shared.errors import ApiError
from app.validation.suites import get_suite


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    release: LabRelease
    created: bool


def _validate(data: dict[str, Any]) -> AppSecLab:
    try:
        manifest = validate_manifest(data)
    except ManifestValidationError as exc:
        raise ApiError(
            400, "VALIDATION_ERROR", "Manifesto inválido.", {"issues": [i.as_dict() for i in exc.issues]}
        ) from exc
    # Regra 6 de docs/11 §3: todo validatorRef deve existir no registro protegido de validadores.
    issues = [
        {
            "path": f"steps.{i}.validatorRef",
            "code": "UNKNOWN_VALIDATOR",
            "message": "Validador não registrado.",
        }
        for i, step in enumerate(manifest.steps)
        if get_suite(step.validator_ref) is None
    ]
    if issues:
        raise ApiError(400, "VALIDATION_ERROR", "Manifesto inválido.", {"issues": issues})
    return manifest


def register_release(
    db: Session, *, data: dict[str, Any], actor_id: uuid.UUID, now: datetime
) -> RegistrationResult:
    """Valida e publica uma release. Idempotente por digest; imutável após publicada."""
    manifest = _validate(data)
    digest = canonical_manifest_digest(manifest)
    lab_id, version = manifest.metadata.id, manifest.metadata.version

    existing = db.execute(
        select(LabRelease).where(LabRelease.lab_id == lab_id, LabRelease.version == version)
    ).scalar_one_or_none()
    if existing is not None:
        if existing.manifest_digest == digest:
            return RegistrationResult(existing, created=False)
        raise ApiError(
            409,
            "RELEASE_IMMUTABLE",
            "Esta versão já foi publicada com conteúdo diferente; publique uma nova versão.",
            {"labId": lab_id, "version": version},
        )

    lab = db.get(Lab, lab_id)
    if lab is None:
        db.add(
            Lab(
                id=lab_id,
                title=manifest.metadata.title,
                primary_cwe=manifest.metadata.primary_cwe,
                created_at=now,
            )
        )
    release = LabRelease(
        id=uuid.uuid4(),
        lab_id=lab_id,
        version=version,
        manifest_digest=digest,
        manifest=manifest.model_dump(mode="json", by_alias=True, exclude_none=True),
        # Ciclo draft/published/retired completo é IMP-208; na 1ª fatia o registro publica.
        status="published",
        published_at=now,
        created_at=now,
        created_by=actor_id,
    )
    db.add(release)
    for v in manifest.variants:
        db.add(
            LabVariant(
                id=uuid.uuid4(),
                release_id=release.id,
                variant_key=v.id,
                language=v.language,
                framework=v.framework,
                image_digest=v.image,
                runtime_profile=v.runtime_profile,
                ttl_minutes=v.session.ttl_minutes,
                max_renewals=v.session.max_renewals,
            )
        )
    for s in manifest.steps:
        step_id = uuid.uuid4()
        db.add(
            LabStep(
                id=step_id,
                release_id=release.id,
                step_key=s.id,
                position=s.order,
                title=s.title,
                validator_ref=s.validator_ref,
                max_points=s.points,
            )
        )
        for h in s.hints:
            db.add(StepHint(id=uuid.uuid4(), step_id=step_id, level=h.level, content=h.text))
    audit.record(
        db,
        now=now,
        actor_id=str(actor_id),
        action="lab_release.published",
        resource_kind="lab_release",
        resource_id=str(release.id),
        metadata={"lab_id": lab_id, "version": version, "manifest_digest": digest},
    )
    try:
        db.commit()
    except IntegrityError as exc:
        # Corrida com registro concorrente da mesma versão: reavaliar de forma idempotente.
        db.rollback()
        again = db.execute(
            select(LabRelease).where(LabRelease.lab_id == lab_id, LabRelease.version == version)
        ).scalar_one_or_none()
        if again is not None and again.manifest_digest == digest:
            return RegistrationResult(again, created=False)
        raise ApiError(409, "RELEASE_IMMUTABLE", "Conflito ao registrar a versão.") from exc
    return RegistrationResult(release, created=True)


def public_release_view(db: Session, release: LabRelease) -> dict[str, Any]:
    """Visão pública: narrativa, CWE, objetivos, variantes e metadados de etapas.

    Nunca inclui validatorRef, textos de dicas nem instruções de etapas (docs/13 §4).
    """
    m = release.manifest
    variants = db.execute(
        select(LabVariant).where(LabVariant.release_id == release.id).order_by(LabVariant.variant_key)
    ).scalars()
    steps = db.execute(
        select(LabStep).where(LabStep.release_id == release.id).order_by(LabStep.position)
    ).scalars()
    return {
        "labId": release.lab_id,
        "version": release.version,
        "status": release.status,
        "manifestDigest": release.manifest_digest,
        "title": m["metadata"]["title"],
        "primaryCwe": m["metadata"]["primaryCwe"],
        "secondaryCwes": m["metadata"].get("secondaryCwes", []),
        "learning": {
            "difficulty": m["learning"]["difficulty"],
            "estimatedMinutes": m["learning"]["estimatedMinutes"],
            "objectives": m["learning"]["objectives"],
            "story": m["learning"]["story"],
        },
        "variants": [
            {
                "id": v.variant_key,
                "language": v.language,
                "framework": v.framework,
                "ttlMinutes": v.ttl_minutes,
                "maxRenewals": v.max_renewals,
            }
            for v in variants
        ],
        "steps": [
            {"id": s.step_key, "order": s.position, "title": s.title, "points": s.max_points} for s in steps
        ],
        "publishedAt": release.published_at.isoformat() if release.published_at else None,
    }


def list_published(db: Session) -> list[LabRelease]:
    return list(
        db.execute(
            select(LabRelease)
            .where(LabRelease.status == "published")
            .order_by(LabRelease.lab_id, LabRelease.created_at)
        ).scalars()
    )


def get_published(db: Session, lab_id: str, version: str) -> LabRelease | None:
    return db.execute(
        select(LabRelease).where(
            LabRelease.lab_id == lab_id, LabRelease.version == version, LabRelease.status == "published"
        )
    ).scalar_one_or_none()
