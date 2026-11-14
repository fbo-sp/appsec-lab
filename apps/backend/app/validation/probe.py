"""Probe de validação comportamental (somente stdlib). Roda em contêiner efêmero, fora do workspace.

Lê ``/probe/spec.json`` = {"base": "http://host:port", "checks": [...], "logins": [...]} e imprime uma
linha JSON ``{"started": bool, "results": {"<id>": true|false}}``. Não recebe segredos de
infraestrutura; o alvo é uma cópia isolada da aplicação do aluno. Respostas são tratadas como dados não
confiáveis (tamanho limitado).

Verificações autenticadas (ADR-015): cada ``login`` abre uma sessão própria (cookies separados) com
credenciais FICTÍCIAS do laboratório; se ``token_field`` for informado, o valor desse campo da resposta
JSON vira o cabeçalho ``Authorization: Bearer``. Uma verificação com ``as_user`` usa essa sessão; sem
``as_user`` ela roda anônima, sem cookies.
"""

from __future__ import annotations

import http.cookiejar
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

MAX_BODY = 512 * 1024


class _Client:
    def __init__(self) -> None:
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )
        self.headers: dict[str, str] = {}

    def request(self, base: str, item: dict[str, Any]) -> tuple[int, str]:
        url = base + str(item["path"])
        data = None
        headers = dict(self.headers)
        if isinstance(item.get("form"), dict):
            data = urllib.parse.urlencode(item["form"]).encode()
        elif item.get("json") is not None:
            data = json.dumps(item["json"]).encode()
            headers["Content-Type"] = "application/json"
        if isinstance(item.get("headers"), dict):
            headers.update({str(k): str(v) for k, v in item["headers"].items()})
        req = urllib.request.Request(  # noqa: S310 - alvo interno efêmero
            url, data=data, method=str(item.get("method", "GET")), headers=headers
        )
        try:
            with self.opener.open(req, timeout=10) as resp:
                return resp.status, resp.read(MAX_BODY).decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(MAX_BODY).decode("utf-8", "replace")


def _login(base: str, login: dict[str, Any]) -> _Client | None:
    client = _Client()
    try:
        status, body = client.request(base, login)
    except OSError:
        return None
    if status >= 400:
        return None
    field = login.get("token_field")
    if field:
        try:
            token = json.loads(body).get(field)
        except (ValueError, AttributeError):
            return None
        if not isinstance(token, str) or not token:
            return None
        client.headers["Authorization"] = f"Bearer {token}"
    return client


def _status_ok(check: dict[str, Any], status: int) -> bool:
    allowed = check.get("expect_status_in") or []
    if allowed:
        return status in allowed
    return check.get("expect_status") in (None, status)


def run(spec: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    base = str(spec["base"])
    checks = spec["checks"]
    assert isinstance(checks, list)
    # Aguarda a aplicação subir (a cópia acabou de iniciar).
    deadline = time.monotonic() + float(spec.get("wait_seconds", 30))
    started = False
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(base + "/", timeout=2).close()  # noqa: S310
            started = True
            break
        except urllib.error.HTTPError:
            started = True  # respondeu (mesmo com erro HTTP): a aplicação está no ar
            break
        except OSError:
            time.sleep(0.5)
    if not started:
        return False, {}
    # Login falho => as verificações daquele usuário falham (fail closed), as demais seguem.
    users = {str(lg["name"]): _login(base, lg) for lg in spec.get("logins", [])}
    results: dict[str, bool] = {}
    for check in checks:
        user = check.get("as_user")
        client = users.get(str(user)) if user else _Client()
        if client is None:
            results[check["id"]] = False
            continue
        try:
            status, body = client.request(base, check)
        except OSError:
            results[check["id"]] = False
            continue
        ok = _status_ok(check, status)
        ok = ok and all(s in body for s in check.get("contains", []))
        ok = ok and not any(s in body for s in check.get("not_contains", []))
        results[check["id"]] = bool(ok)
    return True, results


if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else "/probe/spec.json", encoding="utf-8") as fh:
        started, results = run(json.load(fh))
        print(json.dumps({"started": started, "results": results}))
