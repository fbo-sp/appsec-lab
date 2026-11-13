"""Indicadores para o administrador (ADR-011). Somente leitura e restrito ao papel admin."""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Float, case, cast, func, select
from sqlalchemy.orm import Session

from app.db.models import LabRelease, LabSession, LabVariant
from app.deps import get_clock, get_db
from app.identity.principal import Principal, require_admin
from app.shared.clock import Clock

router = APIRouter(prefix="/api/v1/admin/metrics", tags=["admin"])


@router.get("/provisioning")
def provisioning_metrics(
    _admin: Annotated[Principal, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    clock: Annotated[Clock, Depends(get_clock)],
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> dict[str, Any]:
    """Tempo de subida do ambiente (solicitação até pronto) por laboratório, versão e variante.

    Falhas contam sessões que terminaram em FAILED; renovações ajudam a calibrar o ``ttlMinutes``.
    """
    since = clock.now() - timedelta(days=days)
    seconds = cast(LabSession.provision_ms, Float) / 1000.0
    rows = db.execute(
        select(
            LabRelease.lab_id,
            LabRelease.version,
            LabVariant.variant_key,
            func.count(LabSession.id),
            func.count(LabSession.provision_ms),
            func.sum(case((LabSession.status == "FAILED", 1), else_=0)),
            func.avg(seconds),
            func.percentile_cont(0.5).within_group(seconds),
            func.percentile_cont(0.95).within_group(seconds),
            func.max(seconds),
            func.sum(LabSession.renewals),
        )
        .join(LabRelease, LabRelease.id == LabSession.release_id)
        .join(LabVariant, LabVariant.id == LabSession.variant_id)
        .where(LabSession.created_at >= since)
        .group_by(LabRelease.lab_id, LabRelease.version, LabVariant.variant_key)
        .order_by(LabRelease.lab_id, LabRelease.version, LabVariant.variant_key)
    ).all()

    def r(v: Any) -> float | None:
        return None if v is None else round(float(v), 2)

    return {
        "since": since.isoformat(),
        "days": days,
        "items": [
            {
                "labId": lab_id,
                "version": version,
                "variantId": variant,
                "sessions": total,
                "ready": n_ready,
                "failed": int(failed or 0),
                "provisionSeconds": {"avg": r(avg), "p50": r(p50), "p95": r(p95), "max": r(mx)},
                "renewals": int(renewals or 0),
            }
            for lab_id, version, variant, total, n_ready, failed, avg, p50, p95, mx, renewals in rows
        ],
    }
