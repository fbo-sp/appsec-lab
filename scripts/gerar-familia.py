"""Gera os laboratórios de uma família a partir do modelo comum e dos dados de cada ramo (ADR-021).

Uma família tem a mesma mecânica e o mesmo validador em vários ramos de atividade. O código comum fica
em ``laboratories/_familias/<familia>/modelo/`` e o que muda por ramo (história, nomes do domínio, dados
fictícios) em ``laboratories/_familias/<familia>/ramos.yaml``. O resultado é uma pasta de lab comum e
autocontida (``laboratories/LAB-NNN-...``), que é o que o aluno vê e o que o build usa.

Marcadores no modelo (em conteúdo e em nomes de arquivo):
  [[nome]]     texto do campo ``nome`` do ramo
  [[py:nome]]  o valor como literal Python (listas de registros saem com uma tupla por linha)
Marcador sem valor é erro. Não edite as pastas geradas à mão: edite o modelo ou o ramo e gere de novo.

Uso:  uv run python scripts/gerar-familia.py <familia> [<familia> ...]
      uv run python scripts/gerar-familia.py --check --all     # CI: falha se algo estiver desatualizado
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FAMILIAS = ROOT / "laboratories" / "_familias"
MARK = re.compile(r"\[\[(py:)?([A-Za-z0-9_]+)\]\]")


def _render(text: str, values: dict[str, object], where: str) -> str:
    def rep(m: re.Match[str]) -> str:
        key = m.group(2)
        if key not in values:
            raise SystemExit(f"{where}: marcador sem valor [[{m.group(0)[2:-2]}]]")
        val = values[key]
        if not m.group(1):
            return str(val)
        if isinstance(val, list) and all(isinstance(v, list) for v in val):
            # Lista de registros: uma tupla por linha, legível para o aluno.
            return "[\n" + "".join(f"    {tuple(v)!r},\n" for v in val) + "]"
        return repr(val)

    return MARK.sub(rep, text)


def _values(ramo: dict) -> dict[str, object]:
    vals = dict(ramo["vars"])
    lab = str(vals["lab_id"])
    # Digest FIXTURE (sha256 de um texto fixo); lab-local troca pela imagem construída localmente.
    vals.setdefault("digest_fixture", hashlib.sha256(f"cecyber-fixture:{lab}".encode()).hexdigest())
    return vals


def generate(familia: str) -> dict[Path, str]:
    base = FAMILIAS / familia
    ramos = yaml.safe_load((base / "ramos.yaml").read_text(encoding="utf-8"))["ramos"]
    out: dict[Path, str] = {}
    model = base / "modelo"
    for ramo in ramos:
        vals = _values(ramo)
        dest = ROOT / "laboratories" / ramo["destino"]
        for src in sorted(p for p in model.rglob("*") if p.is_file()):
            rel = _render(str(src.relative_to(model)), vals, str(src))
            out[dest / rel] = _render(src.read_text(encoding="utf-8"), vals, f"{ramo['destino']}/{rel}")
    return out


def main(argv: list[str]) -> int:
    check = "--check" in argv
    names = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        names = sorted(p.name for p in FAMILIAS.iterdir() if (p / "ramos.yaml").is_file())
    if not names:
        print(__doc__)
        return 2
    stale: list[str] = []
    for fam in names:
        files = generate(fam)
        dests = {p.relative_to(ROOT / "laboratories").parts[0] for p in files}
        expected = set(files)
        for d in dests:
            for existing in (ROOT / "laboratories" / d).rglob("*"):
                if existing.is_file() and existing not in expected and "__pycache__" not in existing.parts:
                    stale.append(f"sobra (não está no modelo): {existing.relative_to(ROOT)}")
                    if not check:
                        existing.unlink()
        for path, content in files.items():
            current = path.read_text(encoding="utf-8") if path.is_file() else None
            if current != content:
                stale.append(f"desatualizado: {path.relative_to(ROOT)}")
                if not check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8", newline="\n")
    if check and stale:
        print("Labs gerados desatualizados; rode scripts/gerar-familia.py:\n" + "\n".join(stale))
        return 1
    if not check:
        print(f"{len(stale)} arquivo(s) atualizado(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
