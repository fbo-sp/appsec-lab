"""Probe de validação comportamental (somente stdlib). Roda em contêiner efêmero, fora do workspace.

Lê ``/probe/spec.json`` = {"base": "http://host:port", "checks": [...], "logins": [...]} e imprime uma
linha JSON ``{"started": bool, "results": {"<id>": true|false}}``. Não recebe segredos de
infraestrutura; o alvo é uma cópia isolada da aplicação do aluno. Respostas são tratadas como dados não
confiáveis (tamanho limitado).

Verificações autenticadas (ADR-015): cada ``login`` abre uma sessão própria (cookies separados) com
credenciais FICTÍCIAS do laboratório; se ``token_field`` for informado, o valor desse campo da resposta
JSON vira o cabeçalho ``Authorization: Bearer``. Uma verificação com ``as_user`` usa essa sessão; sem
``as_user`` ela roda anônima, sem cookies.

ADR-023: ``expect_headers`` exige trechos em cabeçalhos da resposta; ``capture`` guarda um valor do corpo
(regex com um grupo) para as verificações seguintes, que o usam como ``{{nome}}``; ``multipart`` envia um
arquivo. Variável ausente ou captura sem casamento => a verificação falha (fail closed).
"""

from __future__ import annotations

import http.cookiejar
import json
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

MAX_BODY = 512 * 1024
_VAR = re.compile(r"\{\{([a-z0-9_]+)\}\}")


class MissingVariableError(Exception):
    """Verificação usa uma variável que nenhuma captura anterior definiu."""


def _fill(value: Any, env: dict[str, str]) -> Any:
    if isinstance(value, str):

        def rep(m: re.Match[str]) -> str:
            if m.group(1) not in env:
                raise MissingVariableError(m.group(1))
            return env[m.group(1)]

        return _VAR.sub(rep, value)
    if isinstance(value, dict):
        return {k: _fill(v, env) for k, v in value.items()}
    if isinstance(value, list):
        return [_fill(v, env) for v in value]
    return value


def _multipart(fields: dict[str, Any], file: dict[str, Any]) -> tuple[bytes, str]:
    boundary = "cecyber" + secrets.token_hex(12)
    out = b""
    for name, val in fields.items():
        out += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode()
    out += (
        f'--{boundary}\r\nContent-Disposition: form-data; name="{file["field"]}"; '
        f'filename="{file["filename"]}"\r\nContent-Type: {file["content_type"]}\r\n\r\n'
    ).encode()
    content = file.get("content", "")
    out += content.encode("latin-1") if isinstance(content, str) else bytes(content)
    out += f"\r\n--{boundary}--\r\n".encode()
    return out, f"multipart/form-data; boundary={boundary}"


class _Client:
    def __init__(self) -> None:
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )
        self.headers: dict[str, str] = {}

    def request(self, base: str, item: dict[str, Any]) -> tuple[int, str, dict[str, str]]:
        url = base + str(item["path"])
        data = None
        headers = dict(self.headers)
        if isinstance(item.get("multipart"), dict):
            data, ctype = _multipart(item.get("form") or {}, item["multipart"])
            headers["Content-Type"] = ctype
        elif isinstance(item.get("form"), dict):
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
                hdrs = {k.lower(): v for k, v in resp.headers.items()}
                return resp.status, resp.read(MAX_BODY).decode("utf-8", "replace"), hdrs
        except urllib.error.HTTPError as exc:
            hdrs = {k.lower(): v for k, v in exc.headers.items()}
            return exc.code, exc.read(MAX_BODY).decode("utf-8", "replace"), hdrs


def _login(base: str, login: dict[str, Any]) -> _Client | None:
    client = _Client()
    try:
        status, body, _ = client.request(base, login)
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


def _headers_ok(check: dict[str, Any], headers: dict[str, str]) -> bool:
    for name, part in (check.get("expect_headers") or {}).items():
        if str(part).lower() not in headers.get(str(name).lower(), "").lower():
            return False
    return True


def _capture(check: dict[str, Any], body: str, env: dict[str, str]) -> bool:
    for name, pattern in (check.get("capture") or {}).items():
        m = re.search(str(pattern), body)
        if m is None or not m.group(1):
            return False
        env[str(name)] = m.group(1)
    return True


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
    env: dict[str, str] = {}  # valores capturados (ADR-023), compartilhados entre usuários
    for check in checks:
        user = check.get("as_user")
        client = users.get(str(user)) if user else _Client()
        if client is None:
            results[check["id"]] = False
            continue
        try:
            item = _fill(check, env)
            status, body, headers = client.request(base, item)
        except (OSError, MissingVariableError):
            results[check["id"]] = False
            continue
        ok = _status_ok(check, status)
        ok = ok and all(s in body for s in item.get("contains", []))
        ok = ok and not any(s in body for s in item.get("not_contains", []))
        ok = ok and _headers_ok(item, headers)
        # Só respostas aprovadas alimentam capturas.
        ok = ok and _capture(check, body, env)
        results[check["id"]] = bool(ok)
    return True, results


if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else "/probe/spec.json", encoding="utf-8") as fh:
        started, results = run(json.load(fh))
        print(json.dumps({"started": started, "results": results}))
