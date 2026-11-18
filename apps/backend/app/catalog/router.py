from __future__ import annotations

from typing import Annotated, Any

import yaml
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.catalog import service
from app.deps import get_clock, get_db
from app.identity.principal import Principal, get_principal, require_admin
from app.shared.clock import Clock
from app.shared.errors import ApiError, not_found

router = APIRouter(prefix="/api/v1", tags=["catalog"])
MAX_MANIFEST_BYTES = 256 * 1024


async def _read_manifest(request: Request) -> dict[str, Any]:
    raw = await request.body()
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ApiError(413, "PAYLOAD_TOO_LARGE", "Manifesto excede o tamanho máximo.")
    ctype = request.headers.get("content-type", "").split(";")[0].strip().lower()
    try:
        if ctype in ("application/yaml", "application/x-yaml", "text/yaml"):
            data = yaml.safe_load(raw)
        elif ctype == "application/json":
            import json

            data = json.loads(raw)
        else:
            raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "Use application/json ou application/yaml.")
    except (yaml.YAMLError, ValueError) as exc:
        raise ApiError(400, "VALIDATION_ERROR", "Manifesto mal formado.") from exc
    if not isinstance(data, dict):
        raise ApiError(400, "VALIDATION_ERROR", "Manifesto deve ser um objeto.")
    return data


@router.post("/admin/lab-releases", status_code=201)
async def register_release(
    request: Request,
    response: Response,
    admin: Annotated[Principal, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    clock: Annotated[Clock, Depends(get_clock)],
) -> dict[str, Any]:
    data = await _read_manifest(request)
    result = service.register_release(db, data=data, actor_id=admin.user_id, now=clock.now())
    if not result.created:
        response.status_code = 200
    return service.public_release_view(db, result.release)


@router.get("/labs")
def list_labs(
    _: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    # Filtro por atribuição/turma (BR-001) é IMP-204. Lista a última versão publicada de cada lab (ADR-016).
    items = [service.public_release_view(db, r) for r in service.list_latest_published(db)]
    return {"items": items}


@router.get("/labs/{lab_id}/releases/{version}")
def get_release(
    lab_id: str,
    version: str,
    _: Annotated[Principal, Depends(get_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    release = service.get_published(db, lab_id, version)
    if release is None:
        raise not_found("Laboratório")
    return service.public_release_view(db, release)
