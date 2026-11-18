"""Site do atacante (ADR-022) e isolamento entre as origens do gateway, contra upstreams falsos."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from aiohttp import DummyCookieJar, web
from aiohttp.test_utils import TestClient, TestServer
from app.gateway.app import AT_COOKIE, PV_COOKIE, WS_COOKIE, GatewayConfig, build_gateway_apps
from app.gateway.tickets import Purpose

from tests.test_unit_gateway import ORIGIN, SECRET, SID, USER, Resolver, _target, _ticket

SEEN: web.AppKey[list[dict[str, str]]] = web.AppKey("seen_attacker", list)
PREVIEW = "http://pv.test"

Scenario = Callable[[TestClient, TestClient, TestClient, web.Application], Awaitable[None]]


def _upstream() -> web.Application:
    seen: list[dict[str, str]] = []

    async def page(request: web.Request) -> web.Response:
        seen.append(dict(request.headers))
        return web.Response(text="<h1>Promoção imperdível</h1>", content_type="text/html")

    async def files(request: web.Request) -> web.Response:
        return web.json_response({"entries": []})

    app = web.Application()
    app[SEEN] = seen
    app.router.add_get("/", page)
    app.router.add_get("/files", files)
    return app


def run(scenario: Scenario) -> None:
    async def main() -> None:
        upstream = _upstream()
        up = TestServer(upstream)
        await up.start_server()
        assert up.port is not None
        resolver = Resolver({SID: _target(SID, USER, up.port)})
        cfg = GatewayConfig(
            SECRET, ORIGIN, PREVIEW, "http://portal.test", agent_port=up.port, attacker_port=up.port
        )
        apps = build_gateway_apps(cfg, resolver)
        servers = [TestServer(a) for a in apps]
        for srv in servers:
            await srv.start_server(access_log=None)
        ws_srv, pv_srv, at_srv = servers
        async with (
            TestClient(ws_srv, cookie_jar=DummyCookieJar()) as ws,
            TestClient(pv_srv, cookie_jar=DummyCookieJar()) as pv,
            TestClient(at_srv, cookie_jar=DummyCookieJar()) as at,
        ):
            await scenario(ws, pv, at, upstream)
        await up.close()

    asyncio.run(main())


async def _login_at(at: TestClient) -> str:
    r = await at.get(
        "/__cecyber/auth", params={"ticket": _ticket(purpose=Purpose.ATTACKER)}, allow_redirects=False
    )
    assert r.status == 303, await r.text()
    # A página do atacante recebe a origem do preview (alvo) pela query string.
    assert r.headers["Location"] == "/?alvo=http%3A%2F%2Fpv.test"
    morsel = r.cookies[AT_COOKIE]
    assert morsel["httponly"] and morsel["samesite"] == "Strict" and morsel["path"] == "/"
    return morsel.value


def test_attacker_site_serves_pages_without_any_browser_cookie() -> None:
    async def s(ws: TestClient, pv: TestClient, at: TestClient, up: web.Application) -> None:
        grant = await _login_at(at)
        r = await at.get("/", headers={"Cookie": f"{AT_COOKIE}={grant}; sessao_do_lab=vitima; {PV_COOKIE}=x"})
        assert r.status == 200
        assert "Promoção" in await r.text()
        assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
        # Nem o cookie da aplicação do lab nem os grants chegam ao site do atacante.
        assert "Cookie" not in up[SEEN][-1]

    run(s)


def test_attacker_site_requires_its_own_grant_and_only_serves_pages() -> None:
    async def s(ws: TestClient, pv: TestClient, at: TestClient, up: web.Application) -> None:
        assert (await at.get("/")).status == 403
        # Ticket de preview não abre o site do atacante (finalidade diferente).
        r = await at.get("/__cecyber/auth", params={"ticket": _ticket(purpose=Purpose.PREVIEW)})
        assert r.status == 401
        grant = await _login_at(at)
        r = await at.post("/", headers={"Cookie": f"{AT_COOKIE}={grant}"}, data="x=1")
        assert r.status == 405
        # O grant do atacante não abre o preview nem o workspace.
        assert (await pv.get("/", headers={"Cookie": f"{PV_COOKIE}={grant}"})).status == 403
        r = await ws.get(
            f"/s/{SID}/__cecyber/api/files",
            headers={"Cookie": f"{WS_COOKIE}={grant}", "X-Cecyber-Workspace": "1"},
        )
        assert r.status == 403

    run(s)


def test_preview_origin_cannot_use_workspace_api_or_terminal() -> None:
    """Isolamento (ADR-022): JavaScript de um lab de XSS roda na origem do preview. O preflight CORS
    para a API do workspace não recebe permissão, e o terminal recusa a origem do preview."""

    async def s(ws: TestClient, pv: TestClient, at: TestClient, up: web.Application) -> None:
        r = await ws.get(f"/s/{SID}/__cecyber/auth", params={"ticket": _ticket()}, allow_redirects=False)
        grant = r.cookies[WS_COOKIE].value
        pre = await ws.options(
            f"/s/{SID}/__cecyber/api/files",
            headers={
                "Origin": PREVIEW,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "x-cecyber-workspace",
                "Cookie": f"{WS_COOKIE}={grant}",
            },
        )
        assert "Access-Control-Allow-Origin" not in pre.headers
        assert "Access-Control-Allow-Headers" not in pre.headers
        # Requisição "simples" (sem o cabeçalho do workspace, que exigiria preflight) é negada.
        simple = await ws.get(
            f"/s/{SID}/__cecyber/api/files", headers={"Origin": PREVIEW, "Cookie": f"{WS_COOKIE}={grant}"}
        )
        assert simple.status == 403
        term = await ws.get(
            f"/s/{SID}/__cecyber/term",
            headers={
                "Origin": PREVIEW,
                "Cookie": f"{WS_COOKIE}={grant}",
                "Connection": "Upgrade",
                "Upgrade": "websocket",
                "Sec-WebSocket-Version": "13",
                "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
            },
        )
        assert term.status == 403

    run(s)
