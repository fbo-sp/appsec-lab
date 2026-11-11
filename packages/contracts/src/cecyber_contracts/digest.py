"""Digest canônico de manifesto: sha256 do JSON normalizado (chaves ordenadas, sem espaços)."""

from __future__ import annotations

import hashlib
import json

from cecyber_contracts.manifest import AppSecLab


def canonical_manifest_json(manifest: AppSecLab) -> str:
    data = manifest.model_dump(mode="json", by_alias=True, exclude_none=True)
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_manifest_digest(manifest: AppSecLab) -> str:
    raw = canonical_manifest_json(manifest).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()
