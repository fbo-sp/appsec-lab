"""Gera docs/catalogo/CATALOGO_DE_LABORATORIOS.md a partir dos manifestos e do histórico (ADR-017).

Uso:  uv run python scripts/gen-catalogo.py           # regenera o catálogo
      uv run python scripts/gen-catalogo.py --check   # CI: falha se estiver desatualizado
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LABS = ROOT / "laboratories"
HISTORY = ROOT / "docs" / "catalogo" / "historico-versoes.yaml"
OUT = ROOT / "docs" / "catalogo" / "CATALOGO_DE_LABORATORIOS.md"
INTERNAL = {"LAB-000"}  # lab benigno de verificação do motor: fora do catálogo para aulas
INTRO = [
    "> Arquivo **gerado** por `scripts/gen-catalogo.py` a partir dos manifestos em `laboratories/`",
    "> e do histórico em `docs/catalogo/historico-versoes.yaml`. Não edite à mão: ao criar um lab ou",
    "> publicar uma versão, atualize o histórico e rode o script. O CI falha se o catálogo estiver",
    "> desatualizado (ADR-017).",
    "",
    "Para professores e área comercial: escolha o laboratório pela aula conceitual (OWASP,",
    "SANS CWE Top 25 ou CWE). Edições de referência: OWASP Top 10 2025 (anterior 2021),",
    "OWASP API Security Top 10 2023 (anterior 2019) e SANS CWE Top 25 2025 (anterior 2024),",
    "publicada pela MITRE com a CISA. Quando o lab não se enquadra numa lista, o CWE orienta a escolha.",
]
DIFFICULTY = {"beginner": "Iniciante", "intermediate": "Intermediário", "advanced": "Avançado"}


def _semver(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def _load() -> tuple[list[dict], dict[str, list[dict]]]:
    manifests = []
    for path in sorted(LABS.glob("LAB-*/manifest.yaml")):
        manifests.append(yaml.safe_load(path.read_text(encoding="utf-8")))
    history = yaml.safe_load(HISTORY.read_text(encoding="utf-8"))["labs"]
    errors = []
    for m in manifests:
        lab, version = m["metadata"]["id"], m["metadata"]["version"]
        versions = [str(h["version"]) for h in history.get(lab, [])]
        if not versions or versions[-1] != version:
            errors.append(f"{lab}@{version}: registre essa versão por último em {HISTORY.relative_to(ROOT)}")
        if versions != sorted(versions, key=_semver):
            errors.append(f"{lab}: versões fora de ordem no histórico")
    if errors:
        sys.exit("\n".join(errors))
    return manifests, history


def _classification_lines(meta: dict) -> list[str]:
    cwes = [
        meta["primaryCwe"] + (" (principal)" if meta.get("secondaryCwes") else ""),
        *meta.get("secondaryCwes", []),
    ]
    lines = [f"- CWE: {', '.join(cwes)}"]
    for c in meta.get("classifications") or []:
        lines.append(f"- {c['framework']} {c['edition']}: {'; '.join(c['entries'])}")
    return lines


def _first(meta: dict, framework: str) -> str:
    for c in meta.get("classifications") or []:
        if c["framework"] == framework:
            return f"{c['entries'][0].replace(' (principal)', '')} ({c['edition']})"
    return "—"


def _history_table(entries: list[dict], current: str) -> list[str]:
    rows = ["| Versão | Criada em | Obsoleta em | Situação | O que mudou |", "|---|---|---|---|---|"]
    for i, h in enumerate(entries):
        nxt = entries[i + 1]["published"] if i + 1 < len(entries) else None
        state = "vigente" if str(h["version"]) == current else "obsoleta"
        rows.append(f"| {h['version']} | {h['published']} | {nxt or '—'} | {state} | {h['summary']} |")
    return rows


def render() -> str:
    manifests, history = _load()
    public = [m for m in manifests if m["metadata"]["id"] not in INTERNAL]
    out = [
        "# Catálogo de laboratórios — CECyber AppSec Labs",
        "",
        *INTRO,
        "",
        "## Visão geral (versões vigentes)",
        "",
        "| Lab | Título | Versão | CWE principal | OWASP Top 10 | SANS CWE Top 25 | Nível | Duração |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for m in public:
        md, lr = m["metadata"], m["learning"]
        level = DIFFICULTY.get(lr["difficulty"], lr["difficulty"])
        out.append(
            f"| {md['id']} | {md['title']} | {md['version']} | {md['primaryCwe']} | "
            f"{_first(md, 'OWASP Top 10')} | {_first(md, 'SANS CWE Top 25')} | {level} | "
            f"{lr['estimatedMinutes']} min |"
        )
    for m in public:
        md, lr = m["metadata"], m["learning"]
        stacks = ", ".join(f"{v['language']} / {v['framework']}" for v in m["variants"])
        out += [
            "",
            f"## {md['id']} · {md['title']}",
            "",
            f"- Versão vigente: {md['version']}",
            f"- Cenário: {lr['story']['application']}",
            f"- Papel do aluno: {lr['story']['role']}",
            f"- Linguagem / stack: {stacks}",
            f"- Nível: {DIFFICULTY.get(lr['difficulty'], lr['difficulty'])}"
            f" · duração estimada: {lr['estimatedMinutes']} min",
            "",
            "### Classificação",
            "",
            *_classification_lines(md),
            "",
            "### Objetivos",
            "",
            *[f"- {o}" for o in lr["objectives"]],
            "",
            "### Etapas",
            "",
            *[f"{i}. {s['title']} ({s['points']} pts)" for i, s in enumerate(m["steps"], start=1)],
            "",
            "### Histórico de versões",
            "",
            *_history_table(history[md["id"]], md["version"]),
        ]
    internal = [m for m in manifests if m["metadata"]["id"] in INTERNAL]
    if internal:
        out += ["", "## Uso interno (fora do catálogo de aulas)", ""]
        for m in internal:
            md = m["metadata"]
            out += [
                f"### {md['id']} · {md['title']}",
                "",
                "Lab benigno de verificação do motor (sem vulnerabilidade), usado em testes da plataforma.",
                "",
                *_history_table(history[md["id"]], md["version"]),
            ]
    return "\n".join(out) + "\n"


def main() -> None:
    text = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            sys.exit(f"{OUT.relative_to(ROOT)} desatualizado: rode `uv run python scripts/gen-catalogo.py`.")
        print("catálogo em dia")
        return
    OUT.write_text(text, encoding="utf-8")
    print(f"gerado {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
