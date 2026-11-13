"""Probe de validação (ADR-010/ADR-015): sessões por usuário, token Bearer e status aceitos."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from app.validation import probe
from app.validation.suites import HttpCheck, HttpLogin, HttpSuite


class _App(BaseHTTPRequestHandler):
    """Aplicação mínima: login por formulário (cookie) e por JSON (token)."""

    def log_message(self, *args: object) -> None:  # silencia o servidor de teste
        pass

    def _send(self, status: int, body: str, headers: dict[str, str] | None = None) -> None:
        data = body.encode()
        self.send_response(status)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        cookie = self.headers.get("Cookie", "")
        auth = self.headers.get("Authorization", "")
        if self.path == "/":
            self._send(200, "ok")
        elif self.path == "/eu":
            who = cookie.removeprefix("quem=") if cookie.startswith("quem=") else "anonimo"
            self._send(200, f"usuario={who}")
        elif self.path == "/api":
            self._send(200 if auth == "Bearer tok-123" else 401, auth or "sem token")
        else:
            self._send(404, "nao encontrado")

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode()
        if self.path == "/login":
            who = body.split("usuario=")[1].split("&")[0]
            self._send(302, "", {"Set-Cookie": f"quem={who}; Path=/", "Location": "/eu"})
        elif self.path == "/api/login":
            ok = json.loads(body).get("senha") == "certa"
            self._send(200 if ok else 401, json.dumps({"token": "tok-123"} if ok else {"erro": "x"}))
        else:
            self._send(404, "")

    def do_PATCH(self) -> None:
        self._send(405, "metodo")


@pytest.fixture(scope="module")
def base() -> Iterator[str]:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _App)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{srv.server_address[1]}"
    finally:
        srv.shutdown()


def _run(base: str, suite: HttpSuite) -> dict[str, bool]:
    started, results = probe.run(
        {"base": base, "checks": suite.probe_checks(), "logins": suite.probe_logins(), "wait_seconds": 5}
    )
    assert started
    return results


def test_each_user_has_its_own_cookie_session_and_anonymous_has_none(base: str) -> None:
    suite = HttpSuite(
        ref="t",
        version="1",
        logins=(
            HttpLogin(name="ana", path="/login", form={"usuario": "ana"}),
            HttpLogin(name="bia", path="/login", form={"usuario": "bia"}),
        ),
        checks=(
            HttpCheck(id="ana", description="", path="/eu", as_user="ana", contains=("usuario=ana",)),
            HttpCheck(id="bia", description="", path="/eu", as_user="bia", contains=("usuario=bia",)),
            HttpCheck(id="anon", description="", path="/eu", contains=("usuario=anonimo",)),
        ),
    )
    assert _run(base, suite) == {"ana": True, "bia": True, "anon": True}


def test_token_login_sets_bearer_and_explicit_headers_override(base: str) -> None:
    suite = HttpSuite(
        ref="t",
        version="1",
        logins=(
            HttpLogin(name="api", path="/api/login", json={"senha": "certa"}, token_field="token"),
            HttpLogin(name="falha", path="/api/login", json={"senha": "errada"}, token_field="token"),
        ),
        checks=(
            HttpCheck(id="token", description="", path="/api", as_user="api"),
            HttpCheck(
                id="forjado",
                description="",
                path="/api",
                headers={"Authorization": "Bearer x"},
                expect_status_in=(401, 403),
            ),
            HttpCheck(id="login-falhou", description="", path="/", as_user="falha"),
            HttpCheck(id="status-lista", description="", path="/nada", expect_status_in=(403, 404)),
            HttpCheck(id="status-errado", description="", path="/nada", expect_status=200),
            HttpCheck(
                id="patch", description="", path="/api", method="PATCH", json={"a": 1}, expect_status=405
            ),
        ),
    )
    r = _run(base, suite)
    assert r["token"] and r["forjado"] and r["status-lista"] and r["patch"], r
    # Login que falha reprova (fail closed) as verificações daquele usuário; status fora do esperado também.
    assert not r["login-falhou"] and not r["status-errado"], r
