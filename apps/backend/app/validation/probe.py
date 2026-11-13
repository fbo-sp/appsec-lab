"""Probe de validação comportamental (somente stdlib). Roda em contêiner efêmero, fora do workspace.

Lê ``/probe/spec.json`` = {"base": "http://host:port", "checks": [...]} e imprime uma linha JSON
``{"results": {"<id>": true|false}}``. Não recebe segredos de infraestrutura; o alvo é uma cópia
isolada da aplicação do aluno. Respostas são tratadas como dados não confiáveis (tamanho limitado).
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MAX_BODY = 512 * 1024


def _request(base: str, check: dict[str, object]) -> tuple[int, str]:
    url = base + str(check["path"])
    data = None
    form = check.get("form")
    if isinstance(form, dict):
        data = urllib.parse.urlencode(form).encode()
    req = urllib.request.Request(url, data=data, method=str(check.get("method", "GET")))  # noqa: S310
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 - alvo interno efêmero
            return resp.status, resp.read(MAX_BODY).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(MAX_BODY).decode("utf-8", "replace")


def run(spec: dict[str, object]) -> dict[str, bool]:
    base = str(spec["base"])
    checks = spec["checks"]
    assert isinstance(checks, list)
    # Aguarda a aplicação subir (a cópia acabou de iniciar).
    deadline = time.monotonic() + float(spec.get("wait_seconds", 30))  # type: ignore[arg-type]
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(base + "/", timeout=2).close()  # noqa: S310
            break
        except urllib.error.HTTPError:
            break
        except OSError:
            time.sleep(0.5)
    results: dict[str, bool] = {}
    for check in checks:
        try:
            status, body = _request(base, check)
        except OSError:
            results[check["id"]] = False
            continue
        ok = check.get("expect_status") in (None, status)
        ok = ok and all(s in body for s in check.get("contains", []))
        ok = ok and not any(s in body for s in check.get("not_contains", []))
        results[check["id"]] = bool(ok)
    return results


if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else "/probe/spec.json", encoding="utf-8") as fh:
        print(json.dumps({"results": run(json.load(fh))}))
