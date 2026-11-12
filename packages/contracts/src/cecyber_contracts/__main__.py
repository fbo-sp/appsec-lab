"""CLI: ``python -m cecyber_contracts validate <manifest.yaml>`` | ``export-schema <saida.json>``."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cecyber_contracts.digest import canonical_manifest_digest
from cecyber_contracts.manifest import AppSecLab
from cecyber_contracts.validation import ManifestValidationError, load_manifest, validate_manifest


def schema_json() -> str:
    schema = AppSecLab.model_json_schema(by_alias=True)
    schema["$id"] = "https://labs.cecyber.io/schemas/appseclab.v1alpha1.schema.json"
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "validate":
        try:
            manifest = validate_manifest(load_manifest(argv[1]))
        except ManifestValidationError as exc:
            for issue in exc.issues:
                print(f"ERRO {issue.loc} [{issue.code}] {issue.message}", file=sys.stderr)
            return 1
        print(f"OK {manifest.metadata.id}@{manifest.metadata.version} {canonical_manifest_digest(manifest)}")
        return 0
    if len(argv) == 2 and argv[0] == "export-schema":
        Path(argv[1]).write_text(schema_json(), encoding="utf-8")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
