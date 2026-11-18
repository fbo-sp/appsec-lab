"""Probe (ADR-023): cabeçalhos exigidos, captura de valor entre verificações e envio multipart."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from app.validation import probe
from app.validation.suites import HttpCheck, HttpLogin, HttpSuite

TOKEN = "tok-abc-123"


class _App(BaseHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
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
        if self.path in ("/", "/form"):
            self._send(200, f'<input type="hidden" name="csrf" value="{TOKEN}">')
        elif self.path == "/arquivo":
            self._send(
                200,
                "pdf",
                {"Content-Disposition": "attachment; filename=a.pdf", "X-Content-Type-Options": "nosniff"},
            )
        else:
            self._send(404, "")

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("latin-1")
        if self.path == "/login":
            self._send(302, "", {"Set-Cookie": "s=1; Path=/", "Location": "/"})
        elif self.path == "/acao":
            self._send(200 if f"csrf={TOKEN}" in body else 403, "feito" if TOKEN in body else "negado")
        elif self.path == "/upload":
            ctype = self.headers.get("Content-Type", "")
            ok = ctype.startswith("multipart/form-data; boundary=") and 'filename="x.png"' in body
            ok = ok and "Content-Type: image/png" in body and "<script>" in body and 'name="nota"' in body
            self._send(201 if ok else 400, "recebido" if ok else "ruim")
        else:
            self._send(404, "")


@pytest.fixture(scope="module")
def base() -> Iterator[str]:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _App)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _run(base: str, suite: HttpSuite) -> dict[str, bool]:
    started, results = probe.run(
        {"base": base, "checks": suite.probe_checks(), "logins": suite.probe_logins(), "wait_seconds": 5}
    )
    assert started
    return results


def test_capture_feeds_later_checks_and_missing_variable_fails(base: str) -> None:
    suite = HttpSuite(
        ref="t/x/capture-v1",
        version="1",
        logins=(HttpLogin(name="ana", path="/login", form={"u": "ana"}),),
        checks=(
            HttpCheck(
                id="sem-variavel", description="d", path="/acao", method="POST", form={"csrf": "{{tk}}"}
            ),
            HttpCheck(
                id="captura", description="d", path="/form", as_user="ana", capture={"tk": r'value="([^"]+)"'}
            ),
            HttpCheck(
                id="usa",
                description="d",
                path="/acao",
                method="POST",
                form={"csrf": "{{tk}}"},
                contains=("feito",),
            ),
            HttpCheck(
                id="captura-falha", description="d", path="/form", capture={"x": r'nao-existe="(\w+)"'}
            ),
            HttpCheck(
                id="sem-token", description="d", path="/acao", method="POST", form={}, expect_status=403
            ),
        ),
    )
    assert _run(base, suite) == {
        "sem-variavel": False,
        "captura": True,
        "usa": True,
        "captura-falha": False,
        "sem-token": True,
    }


def test_expect_headers_is_case_insensitive_and_strict_on_absence(base: str) -> None:
    suite = HttpSuite(
        ref="t/x/headers-v1",
        version="1",
        checks=(
            HttpCheck(
                id="ok",
                description="d",
                path="/arquivo",
                expect_headers={"content-disposition": "ATTACHMENT", "X-Content-Type-Options": "nosniff"},
            ),
            HttpCheck(
                id="ausente", description="d", path="/", expect_headers={"Content-Security-Policy": "default"}
            ),
        ),
    )
    assert _run(base, suite) == {"ok": True, "ausente": False}


def test_multipart_upload_with_extra_fields(base: str) -> None:
    suite = HttpSuite(
        ref="t/x/upload-v1",
        version="1",
        checks=(
            HttpCheck(
                id="envio",
                description="d",
                path="/upload",
                method="POST",
                form={"nota": "comprovante"},
                multipart={
                    "field": "arquivo",
                    "filename": "x.png",
                    "content_type": "image/png",
                    "content": "<script>",
                },
                expect_status=201,
            ),
        ),
    )
    assert _run(base, suite) == {"envio": True}
