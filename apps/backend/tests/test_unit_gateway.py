"""Gateway de workspace (IMP-302) contra upstreams falsos: autenticação, revogação e isolamento."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta

import pytest
from aiohttp import DummyCookieJar, WSMsgType, web
from aiohttp.test_utils import TestClient, TestServer
from app.gateway.app import PV_COOKIE, WS_COOKIE, GatewayConfig, build_apps
from app.gateway.resolver import SessionTarget
from app.gateway.tickets import Audience, Purpose, issue

SECRET = "gateway-unit-test-secret-0123456789abcdef"
SID, OTHER = "11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"
USER, INTRUDER = "user-a", "user-b"
ORIGIN = "http://ws.test"


@dataclass
class Resolver:
    targets: dict[str, SessionTarget] = field(default_factory=dict)

    def resolve(self, session_id: str) -> SessionTarget | None:
        return self.targets.get(session_id)


def _target(sid: str, user: str, port: int, status: str = "ACTIVE") -> SessionTarget:
    return SessionTarget(sid, user, status, datetime.now(UTC) + timedelta(minutes=10), "127.0.0.1", port)


def _ticket(
    sid: str = SID, user: str = USER, purpose: Purpose = Purpose.WORKSPACE, secret: str = SECRET
) -> str:
    token, _ = issue(
        secret, sid=sid, sub=user, purpose=purpose, aud=Audience.TICKET, now=datetime.now(UTC), ttl_seconds=60
    )
    return token


SEEN: web.AppKey[list[dict[str, str]]] = web.AppKey("seen", list)


def _upstream() -> web.Application:
    """Aplicação do lab e agente de workspace falsos, no mesmo servidor."""
    seen: list[dict[str, str]] = []

    async def app_root(request: web.Request) -> web.Response:
        seen.append(dict(request.headers))
        return web.Response(
            text="<h1>app do lab</h1>",
            content_type="text/html",
            headers={"X-Frame-Options": "DENY", "Set-Cookie": "labsess=1; Path=/"},
        )

    async def files(request: web.Request) -> web.Response:
        seen.append(dict(request.headers))
        return web.json_response(
            {"path": "", "entries": [{"name": "a.py", "path": "a.py", "type": "file", "size": 1}]}
        )

    async def term(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for msg in ws:
            if msg.type is WSMsgType.TEXT:
                await ws.send_str("eco:" + msg.data)
        return ws

    app = web.Application()
    app[SEEN] = seen
    app.router.add_get("/", app_root)
    app.router.add_get("/files", files)
    app.router.add_get("/term", term)
    return app


Scenario = Callable[[TestClient, TestClient, Resolver, web.Application], Awaitable[None]]


def run(scenario: Scenario) -> None:
    async def main() -> None:
        upstream = _upstream()
        up = TestServer(upstream)
        await up.start_server()
        assert up.port is not None
        resolver = Resolver({SID: _target(SID, USER, up.port), OTHER: _target(OTHER, INTRUDER, up.port)})
        cfg = GatewayConfig(SECRET, ORIGIN, "http://pv.test", "http://portal.test", agent_port=up.port)
        ws_app, pv_app = build_apps(cfg, resolver)
        # access_log=None como em app.gateway.run (o log padrão do aiohttp incluiria a query string).
        # Sem cookie jar: cada requisição do teste declara explicitamente os cookies que envia.
        jar1, jar2 = DummyCookieJar(), DummyCookieJar()
        ws_srv, pv_srv = TestServer(ws_app), TestServer(pv_app)
        await ws_srv.start_server(access_log=None)
        await pv_srv.start_server(access_log=None)
        async with (
            TestClient(ws_srv, cookie_jar=jar1) as ws,
            TestClient(pv_srv, cookie_jar=jar2) as pv,
        ):
            await scenario(ws, pv, resolver, upstream)
        await up.close()

    asyncio.run(main())


async def _login_ws(ws: TestClient, sid: str = SID, user: str = USER) -> str:
    r = await ws.get(f"/s/{sid}/__cecyber/auth", params={"ticket": _ticket(sid, user)}, allow_redirects=False)
    assert r.status == 303, await r.text()
    return r.cookies[WS_COOKIE].value


async def _login_pv(pv: TestClient) -> str:
    r = await pv.get(
        "/__cecyber/auth", params={"ticket": _ticket(purpose=Purpose.PREVIEW)}, allow_redirects=False
    )
    assert r.status == 303
    return r.cookies[PV_COOKIE].value


def test_ticket_exchange_sets_scoped_httponly_cookie_and_is_single_use() -> None:
    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        ticket = _ticket()
        r = await ws.get(f"/s/{SID}/__cecyber/auth", params={"ticket": ticket}, allow_redirects=False)
        assert r.status == 303 and r.headers["Location"] == f"/s/{SID}/"
        raw = r.headers["Set-Cookie"]
        assert "HttpOnly" in raw and "SameSite=Strict" in raw and f"Path=/s/{SID}/" in raw
        again = await ws.get(f"/s/{SID}/__cecyber/auth", params={"ticket": ticket}, allow_redirects=False)
        assert again.status == 401

    run(s)


@pytest.mark.parametrize(
    "case", ["wrong_purpose", "wrong_secret", "other_sid_path", "not_owner", "terminated"]
)
def test_ticket_exchange_rejections(case: str) -> None:
    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        sid, ticket = SID, _ticket()
        if case == "wrong_purpose":
            ticket = _ticket(purpose=Purpose.PREVIEW)
        elif case == "wrong_secret":
            ticket = _ticket(secret="x" * 40)
        elif case == "other_sid_path":
            sid = OTHER
        elif case == "not_owner":
            ticket = _ticket(user=INTRUDER)
        else:
            res.targets[SID] = replace(res.targets[SID], status="TERMINATING")
        r = await ws.get(f"/s/{sid}/__cecyber/auth", params={"ticket": ticket}, allow_redirects=False)
        assert r.status in (401, 403)
        assert WS_COOKIE not in r.cookies

    run(s)


def test_workspace_api_requires_grant_header_and_matching_session() -> None:
    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        grant = await _login_ws(ws)
        hdr = {"X-Cecyber-Workspace": "1", "Cookie": f"{WS_COOKIE}={grant}"}
        ok = await ws.get(f"/s/{SID}/__cecyber/api/files", headers=hdr)
        assert ok.status == 200 and (await ok.json())["entries"][0]["name"] == "a.py"
        # O grant não é repassado ao agente (código não confiável).
        assert all(WS_COOKIE not in h.get("Cookie", "") for h in up[SEEN])
        no_header = await ws.get(f"/s/{SID}/__cecyber/api/files", headers={"Cookie": f"{WS_COOKIE}={grant}"})
        assert no_header.status == 403
        no_grant = await ws.get(f"/s/{SID}/__cecyber/api/files", headers={"X-Cecyber-Workspace": "1"})
        assert no_grant.status == 403
        # Grant da sessão A não abre a sessão B (de outro aluno).
        cross = await ws.get(f"/s/{OTHER}/__cecyber/api/files", headers=hdr)
        assert cross.status == 403
        bad_op = await ws.post(f"/s/{SID}/__cecyber/api/files", headers=hdr)
        assert bad_op.status == 405

    run(s)


def test_grant_survives_renewal_but_not_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regressão: o grant valia só até o prazo da emissão; renovar derrubava as abas (GATEWAY_DENIED)."""
    import app.gateway.app as gw

    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        t0 = datetime.now(UTC)
        # 10 min de prazo + 2 renovações de 45 min ainda disponíveis.
        res.targets[SID] = replace(res.targets[SID], max_expires_at=t0 + timedelta(minutes=100))
        r = await pv.get(
            "/__cecyber/auth", params={"ticket": _ticket(purpose=Purpose.PREVIEW)}, allow_redirects=False
        )
        assert r.status == 303
        assert 5900 <= int(r.cookies[PV_COOKIE]["max-age"]) <= 6000
        grant = r.cookies[PV_COOKIE].value
        hdr = {"Cookie": f"{PV_COOKIE}={grant}"}
        # 20 min depois, já após o prazo original, com a sessão renovada até t0+55.
        monkeypatch.setattr(gw, "_now", lambda: t0 + timedelta(minutes=20))
        res.targets[SID] = replace(res.targets[SID], expires_at=t0 + timedelta(minutes=55))
        pv.server.app[gw.STATE].cache.clear()  # o cache de resolução dura 2 s
        ok = await pv.get("/", headers=hdr)
        assert ok.status == 200, await ok.text()
        # Sem nova renovação, o prazo efetivo do banco continua valendo.
        monkeypatch.setattr(gw, "_now", lambda: t0 + timedelta(minutes=56))
        pv.server.app[gw.STATE].cache.clear()
        expired = await pv.get("/", headers=hdr)
        assert expired.status == 403

    run(s)


def test_termination_revokes_existing_grant_immediately() -> None:
    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        grant = await _login_ws(ws)
        hdr = {"X-Cecyber-Workspace": "1", "Cookie": f"{WS_COOKIE}={grant}"}
        assert (await ws.get(f"/s/{SID}/__cecyber/api/files", headers=hdr)).status == 200
        res.targets[SID] = replace(res.targets[SID], status="TERMINATING")
        await asyncio.sleep(2.1)  # cache do resolvedor (2 s)
        assert (await ws.get(f"/s/{SID}/__cecyber/api/files", headers=hdr)).status == 403

    run(s)


def test_terminal_websocket_checks_origin_and_relays() -> None:
    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        grant = await _login_ws(ws)
        cookie = {"Cookie": f"{WS_COOKIE}={grant}"}
        bad = await ws.get(f"/s/{SID}/__cecyber/term", headers={**cookie, "Origin": "http://pv.test"})
        assert bad.status == 403
        conn = await ws.ws_connect(f"/s/{SID}/__cecyber/term", headers={**cookie, "Origin": ORIGIN})
        await conn.send_str('{"t":"i","d":"ls"}')
        msg = await conn.receive(timeout=5)
        assert msg.data == 'eco:{"t":"i","d":"ls"}'
        await conn.close()

    run(s)


def test_preview_proxies_app_without_leaking_gateway_cookie() -> None:
    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        assert (await pv.get("/")).status == 403
        grant = await _login_pv(pv)
        r = await pv.get("/", headers={"Cookie": f"{PV_COOKIE}={grant}; labsess=1"})
        assert r.status == 200 and "app do lab" in await r.text()
        assert r.headers["Cache-Control"] == "no-store"
        assert r.headers["Content-Security-Policy"] == "frame-ancestors http://portal.test"
        assert "X-Frame-Options" not in r.headers
        forwarded = up[SEEN][-1].get("Cookie", "")
        assert forwarded == "labsess=1"  # cookie da aplicação passa; grant do gateway não
        # Grant de workspace não vale no preview.
        ws_grant = await _login_ws(ws)
        assert (await pv.get("/", headers={"Cookie": f"{PV_COOKIE}={ws_grant}"})).status == 403

    run(s)


def test_tickets_never_reach_logs(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="app.gateway")
    tokens: list[str] = []

    async def s(ws: TestClient, pv: TestClient, res: Resolver, up: web.Application) -> None:
        t = _ticket()
        tokens.append(t)
        await ws.get(f"/s/{SID}/__cecyber/auth", params={"ticket": t}, allow_redirects=False)

    run(s)
    text = "\n".join(f"{r.getMessage()} {r.__dict__}" for r in caplog.records)
    assert "gateway.request" in text and tokens[0] not in text
