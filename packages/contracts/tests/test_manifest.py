from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from cecyber_contracts import (
    ManifestValidationError,
    canonical_manifest_digest,
    load_manifest,
    validate_manifest,
)
from cecyber_contracts.__main__ import schema_json

ROOT = Path(__file__).resolve().parents[3]
BENIGN = ROOT / "laboratories" / "LAB-000-hello-benign" / "manifest.yaml"
SCHEMA = ROOT / "packages" / "contracts" / "schemas" / "appseclab.v1alpha1.schema.json"


@pytest.fixture
def manifest() -> dict[str, Any]:
    return load_manifest(BENIGN)


def codes(data: dict[str, Any]) -> set[str]:
    with pytest.raises(ManifestValidationError) as exc:
        validate_manifest(data)
    return {i.code for i in exc.value.issues}


def test_benign_manifest_is_valid(manifest: dict[str, Any]) -> None:
    m = validate_manifest(manifest)
    assert m.metadata.id == "LAB-000"
    assert m.variants[0].network.egress_profile == "deny-all"


def test_schema_file_matches_model() -> None:
    assert SCHEMA.read_text(encoding="utf-8") == schema_json(), (
        "Schema desatualizado: rode `python -m cecyber_contracts export-schema` "
    )


def test_digest_is_stable_and_content_sensitive(manifest: dict[str, Any]) -> None:
    d1 = canonical_manifest_digest(validate_manifest(manifest))
    d2 = canonical_manifest_digest(validate_manifest(copy.deepcopy(manifest)))
    assert d1 == d2 and d1.startswith("sha256:")
    manifest["steps"][0]["hints"][0]["text"] = "Outro texto"
    assert canonical_manifest_digest(validate_manifest(manifest)) != d1


def test_digest_ignores_key_order(manifest: dict[str, Any]) -> None:
    reordered = json.loads(json.dumps(manifest, sort_keys=True))
    assert canonical_manifest_digest(validate_manifest(reordered)) == canonical_manifest_digest(
        validate_manifest(manifest)
    )


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda m: m.update(apiVersion="labs.cecyber.io/v2"), "LITERAL_ERROR"),
        (lambda m: m.update(kind="Other"), "LITERAL_ERROR"),
        (lambda m: m.update(unknownField=1), "EXTRA_FORBIDDEN"),
        (lambda m: m["metadata"].update(status="draft"), "EXTRA_FORBIDDEN"),
        (lambda m: m["metadata"].update(id="lab-1"), "STRING_PATTERN_MISMATCH"),
        (lambda m: m["metadata"].update(version="1.0"), "STRING_PATTERN_MISMATCH"),
        (lambda m: m["metadata"].update(primaryCwe="89"), "STRING_PATTERN_MISMATCH"),
        (lambda m: m["learning"].update(singleVulnerability=False), "LITERAL_ERROR"),
        (lambda m: m["learning"]["story"].pop("mission"), "MISSING"),
        (lambda m: m["variants"][0].update(image="registry.local/labs/x:latest"), "STRING_PATTERN_MISMATCH"),
        (
            lambda m: m["variants"][0].update(image="registry.local/labs/x@sha256:REPLACE_WITH_REAL_DIGEST"),
            "STRING_PATTERN_MISMATCH",
        ),
        (lambda m: m["variants"][0]["startup"].update(command="python app.py"), "TUPLE_TYPE"),
        (lambda m: m["variants"][0]["startup"].update(port=80), "GREATER_THAN_EQUAL"),
        (lambda m: m["variants"][0].update(network={"egressProfile": "allow-all"}), "LITERAL_ERROR"),
        (lambda m: m["variants"][0].update(workspacePath="/etc"), "STRING_PATTERN_MISMATCH"),
        (lambda m: m["variants"][0].update(privileged=True), "EXTRA_FORBIDDEN"),
        (lambda m: m["steps"][0].update(validatorRef="../../etc/passwd"), "STRING_PATTERN_MISMATCH"),
        (lambda m: m["steps"][0]["hints"].append({"level": 4, "text": "x"}), "LESS_THAN_EQUAL"),
        (lambda m: m.update(steps=[]), "TOO_SHORT"),
    ],
)
def test_structural_rejections(manifest: dict[str, Any], mutate: Any, expected: str) -> None:
    mutate(manifest)
    assert expected in codes(manifest)


def _second_step(manifest: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    step = copy.deepcopy(manifest["steps"][0])
    step.update(id="second", order=2, points=0, hints=[])
    step.update(overrides)
    return step


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda m: m["variants"].append(copy.deepcopy(m["variants"][0])), "DUPLICATE_VARIANT_ID"),
        (
            lambda m: m["variants"][0].update(image="registry.local/labs/x@sha256:" + "0" * 64),
            "PLACEHOLDER_DIGEST",
        ),
        (lambda m: m["variants"][0].update(runtimeProfile="does-not-exist"), "UNKNOWN_PROFILE"),
        (lambda m: m["variants"][0].update(runtimeProfile="exec-restricted"), "PROFILE_DISABLED"),
        (lambda m: m["variants"][0]["resources"].update(cpuMillicores=4000), "EXCEEDS_PROFILE"),
        (lambda m: m["variants"][0]["resources"].update(memoryMiB=99999), "EXCEEDS_PROFILE"),
        (lambda m: m["variants"][0]["session"].update(ttlMinutes=600), "EXCEEDS_PROFILE"),
        (lambda m: m["variants"][0].update(interfaces=["editor", "editor"]), "DUPLICATE_INTERFACE"),
        (lambda m: m["metadata"].update(secondaryCwes=[m["metadata"]["primaryCwe"]]), "DUPLICATE_CWE"),
        (lambda m: m["steps"][0].update(points=90), "INVALID_TOTAL_POINTS"),
        (lambda m: m["steps"].append(_second_step(m, id=m["steps"][0]["id"])), "DUPLICATE_STEP_ID"),
        (lambda m: m["steps"].append(_second_step(m, order=3)), "NON_CONTIGUOUS_ORDER"),
        (lambda m: m["steps"][0]["hints"].append({"level": 3, "text": "x"}), "INVALID_HINT_LEVELS"),
        (
            lambda m: (
                m["steps"][0].update(points=50),
                m["steps"].append(_second_step(m, points=50)),
                m["policy"].update(finalPassingScore=100),
                m["steps"][1].update(points=40),
            ),
            "UNREACHABLE_PASSING_SCORE",
        ),
    ],
)
def test_semantic_rejections(manifest: dict[str, Any], mutate: Any, expected: str) -> None:
    mutate(manifest)
    assert expected in codes(manifest)


def test_two_variants_share_steps(manifest: dict[str, Any]) -> None:
    """LEX-006: o modelo aceita múltiplas variantes de linguagem sobre as mesmas etapas."""
    node = copy.deepcopy(manifest["variants"][0])
    node.update(
        id="node-http",
        language="javascript",
        framework="node",
        image="registry.local/labs/lab-000-hello-node@sha256:" + "a1" * 32,
        startup={"command": ["node", "server.js"], "port": 3000},
    )
    manifest["variants"].append(node)
    m = validate_manifest(manifest)
    assert [v.id for v in m.variants] == ["python-http", "node-http"]
    assert len(m.steps) == 1


def test_issues_have_location(manifest: dict[str, Any]) -> None:
    manifest["variants"][0]["resources"]["cpuMillicores"] = 4000
    with pytest.raises(ManifestValidationError) as exc:
        validate_manifest(manifest)
    assert exc.value.issues[0].loc == "variants.0.resources.cpuMillicores"
