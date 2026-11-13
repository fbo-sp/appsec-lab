"""Gateway de workspace LOCAL (IMP-302, ADR-009): único caminho do navegador até a sessão.

Duas origens distintas:
- **workspace** (padrão :8001): interface de editor/terminal e API de arquivos em ``/s/{sid}/``;
- **preview** (padrão :8002): aplicação do laboratório servida na raiz, sessão definida por cookie.
A aplicação (potencialmente vulnerável) nunca compartilha origem com o portal nem com o workspace.

Regras:
- acesso só com ticket de uso único emitido pela API ao dono de sessão READY/ACTIVE, trocado por um
  grant em cookie HttpOnly/SameSite=Strict; cada requisição revalida estado e dono no banco;
- destino resolvido no servidor (``runtime_instances``), nunca a partir de dados do navegador;
- requisições do workspace exigem cabeçalho próprio (força preflight CORS, que o gateway não aceita)
  e WebSocket exige ``Origin`` igual à origem do workspace — proteção contra CSRF a partir do preview;
- tickets/grants nunca são registrados em log (só o caminho, sem query string).
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiohttp
from aiohttp import WSMsgType, web

from app.gateway.resolver import SessionResolver, SessionTarget
from app.gateway.tickets import Audience, Claims, Purpose, TokenError, issue, verify

_log = logging.getLogger("app.gateway")

AGENT_PORT = 7681
ALLOWED_STATUSES = frozenset({"READY", "ACTIVE"})
WS_COOKIE = "cecyber_ws"
PV_COOKIE = "cecyber_pv"
WS_HEADER = "X-Cecyber-Workspace"
GRANT_MAX_SECONDS = 8 * 3600
RECHECK_SECONDS = 5.0
# Atividade do aluno (ADR-014) é gravada no máximo uma vez a cada 30 s por sessão.
ACTIVITY_THROTTLE_SECONDS = 30.0
HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
}


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class GatewayConfig:
    secret: str
    workspace_origin: str
    preview_origin: str
    portal_origin: str
    web_dist: Path | None = None
    secure_cookies: bool = False
    agent_port: int = AGENT_PORT


@dataclass
class _State:
    config: GatewayConfig
    resolver: SessionResolver
    used_jti: dict[str, int] = field(default_factory=dict)
    cache: dict[str, tuple[float, SessionTarget | None]] = field(default_factory=dict)
    http: aiohttp.ClientSession | None = None
    touched: dict[str, float] = field(default_factory=dict)

    async def activity(self, sid: str) -> None:
        """Uso real do editor, terminal ou aplicação conta como atividade; falhas não afetam o tráfego."""
        now = time.monotonic()
        if now - self.touched.get(sid, -1e9) < ACTIVITY_THROTTLE_SECONDS:
            return
        self.touched[sid] = now
        try:
            await asyncio.to_thread(self.resolver.touch, sid)
        except Exception:  # pragma: no cover - banco indisponível não derruba o proxy
            _log.warning(
                "gateway_activity_failed", extra={"event": "gateway.activity_failed", "session_id": sid}
            )

    async def target(self, sid: str, *, fresh: bool = False) -> SessionTarget | None:
        hit = self.cache.get(sid)
        if not fresh and hit and time.monotonic() - hit[0] < 2.0:
            return hit[1]
        t = await asyncio.to_thread(self.resolver.resolve, sid)
        self.cache[sid] = (time.monotonic(), t)
        return t

    def consume(self, claims: Claims) -> bool:
        now = int(time.time())
        for k in [k for k, exp in self.used_jti.items() if exp < now]:
            del self.used_jti[k]
        if claims.jti in self.used_jti:
            return False
        self.used_jti[claims.jti] = claims.exp
        return True


STATE: web.AppKey[_State] = web.AppKey("state", _State)


def _deny(status: int = 403, msg: str = "Sessão indisponível ou acesso não autorizado.") -> web.Response:
    return web.json_response(
        {"error": {"code": "GATEWAY_DENIED", "message": msg}},
        status=status,
        headers={"Cache-Control": "no-store"},
    )


def _usable(t: SessionTarget | None, user: str) -> bool:
    return bool(
        t
        and t.user_id == user
        and t.status in ALLOWED_STATUSES
        and t.expires_at > _now()
        and t.host
        and t.port
    )


async def _authorize(request: web.Request, sid: str, purpose: Purpose, cookie: str) -> SessionTarget | None:
    st = request.app[STATE]
    try:
        claims = verify(
            st.config.secret, request.cookies.get(cookie), aud=Audience.GRANT, purpose=purpose, now=_now()
        )
    except TokenError:
        return None
    if sid and claims.sid != sid:
        return None
    t = await st.target(claims.sid)
    return t if t is not None and _usable(t, claims.sub) else None


async def _exchange(
    request: web.Request, sid: str | None, purpose: Purpose
) -> tuple[str, str, int] | web.Response:
    """Troca ticket (uso único) por grant. Retorna (token, sid, max_age) ou resposta de erro."""
    st = request.app[STATE]
    try:
        claims = verify(
            st.config.secret, request.query.get("ticket"), aud=Audience.TICKET, purpose=purpose, now=_now()
        )
    except TokenError:
        return _deny(401, "Ticket inválido ou vencido. Volte ao portal e abra o laboratório novamente.")
    if sid is not None and claims.sid != sid:
        return _deny(401)
    if not st.consume(claims):
        return _deny(401, "Ticket já utilizado.")
    t = await st.target(claims.sid, fresh=True)
    if t is None or not _usable(t, claims.sub):
        return _deny()
    # Vale até o prazo máximo da sessão (inclui renovações restantes): renovar não derruba as abas.
    # Encerramento/expiração continuam efetivos porque cada requisição revalida estado e prazo no banco.
    limit = t.max_expires_at or t.expires_at
    max_age = max(1, min(GRANT_MAX_SECONDS, int((limit - _now()).total_seconds())))
    token, _ = issue(
        st.config.secret,
        sid=claims.sid,
        sub=claims.sub,
        purpose=purpose,
        aud=Audience.GRANT,
        now=_now(),
        ttl_seconds=max_age,
    )
    _log.info(
        "gateway_grant", extra={"event": "gateway.grant", "session_id": claims.sid, "purpose": purpose.value}
    )
    return token, claims.sid, max_age


def _redirect(location: str, cookie: str, token: str, path: str, max_age: int, secure: bool) -> web.Response:
    resp = web.Response(
        status=303,
        headers={"Location": location, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
    resp.set_cookie(
        cookie, token, path=path, max_age=max_age, httponly=True, samesite="Strict", secure=secure
    )
    return resp


def _forward_headers(request: web.Request, drop_cookie: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in request.headers.items():
        lk = k.lower()
        if (
            lk in HOP
            or lk in ("cookie", "origin", "referer", WS_HEADER.lower())
            or lk.startswith("sec-websocket")
        ):
            continue
        out[k] = v
    cookies = [f"{k}={v}" for k, v in request.cookies.items() if k not in (WS_COOKIE, PV_COOKIE, drop_cookie)]
    if cookies:
        out["Cookie"] = "; ".join(cookies)
    return out


async def _proxy_http(
    request: web.Request,
    url: str,
    *,
    drop_cookie: str,
    extra_headers: dict[str, str] | None = None,
    frame_ancestors: str | None = None,
) -> web.StreamResponse:
    st = request.app[STATE]
    assert st.http is not None
    headers = _forward_headers(request, drop_cookie)
    headers["Host"] = request.host
    try:
        async with st.http.request(
            request.method,
            url,
            headers=headers,
            data=request.content if request.body_exists else None,
            allow_redirects=False,
            timeout=aiohttp.ClientTimeout(total=60, sock_connect=5),
        ) as up:
            resp = web.StreamResponse(status=up.status)
            overrides = extra_headers or {}
            for k, v in up.headers.items():
                if k.lower() in HOP or k.lower() == "x-frame-options" or k in overrides:
                    continue
                resp.headers.add(k, v)
            resp.headers.update(overrides)
            if frame_ancestors:
                # Preserva a CSP da aplicação (pode ser parte do exercício) e só restringe o enquadramento.
                csp = resp.headers.get("Content-Security-Policy")
                if not csp:
                    resp.headers["Content-Security-Policy"] = f"frame-ancestors {frame_ancestors}"
                elif "frame-ancestors" not in csp:
                    resp.headers["Content-Security-Policy"] = f"{csp}; frame-ancestors {frame_ancestors}"
            await resp.prepare(request)
            async for chunk in up.content.iter_chunked(64 * 1024):
                await resp.write(chunk)
            await resp.write_eof()
            return resp
    except (aiohttp.ClientError, TimeoutError):
        return _deny(502, "A aplicação do laboratório não respondeu. Aguarde alguns segundos e recarregue.")


# -- origem do workspace ---------------------------------------------------------------------------
def _ws_security_headers(cfg: GatewayConfig) -> dict[str, str]:
    ws_scheme = cfg.workspace_origin.replace("http", "ws", 1)
    return {
        "Content-Security-Policy": (
            f"default-src 'self'; connect-src 'self' {ws_scheme}; img-src 'self' data:; "
            f"style-src 'self' 'unsafe-inline'; frame-ancestors {cfg.portal_origin}; "
            "base-uri 'none'; form-action 'none'"
        ),
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Cache-Control": "no-store",
    }


async def ws_auth(request: web.Request) -> web.StreamResponse:
    sid = request.match_info["sid"]
    res = await _exchange(request, sid, Purpose.WORKSPACE)
    if isinstance(res, web.Response):
        return res
    token, sid, max_age = res
    cfg = request.app[STATE].config
    return _redirect(f"/s/{sid}/", WS_COOKIE, token, f"/s/{sid}/", max_age, cfg.secure_cookies)


async def ws_page(request: web.Request) -> web.StreamResponse:
    sid = request.match_info["sid"]
    cfg = request.app[STATE].config
    if await _authorize(request, sid, Purpose.WORKSPACE, WS_COOKIE) is None:
        return _deny()
    page = cfg.web_dist / "workspace.html" if cfg.web_dist else None
    if page is None or not page.is_file():
        return web.Response(text="Interface do workspace não instalada (WEB_DIST_DIR).", status=503)
    return web.FileResponse(page, headers=_ws_security_headers(cfg))


async def ws_api(request: web.Request) -> web.StreamResponse:
    sid, op = request.match_info["sid"], request.match_info["op"]
    if request.headers.get(WS_HEADER) != "1":
        return _deny(403, "Cabeçalho do workspace ausente.")
    t = await _authorize(request, sid, Purpose.WORKSPACE, WS_COOKIE)
    if t is None:
        return _deny()
    st = request.app[STATE]
    allowed = {("files", "GET"), ("file", "GET"), ("file", "PUT")}
    if (op, request.method) not in allowed:
        return _deny(405, "Operação não permitida.")
    await st.activity(t.session_id)
    url = f"http://{t.host}:{st.config.agent_port}/{op}?{request.query_string}"
    return await _proxy_http(request, url, drop_cookie=WS_COOKIE, extra_headers={"Cache-Control": "no-store"})


async def ws_terminal(request: web.Request) -> web.StreamResponse:
    sid = request.match_info["sid"]
    st = request.app[STATE]
    if request.headers.get("Origin") != st.config.workspace_origin:
        return _deny(403, "Origem não permitida.")
    t = await _authorize(request, sid, Purpose.WORKSPACE, WS_COOKIE)
    if t is None:
        return _deny()
    claims = verify(
        st.config.secret,
        request.cookies.get(WS_COOKIE),
        aud=Audience.GRANT,
        purpose=Purpose.WORKSPACE,
        now=_now(),
    )
    assert st.http is not None
    client = web.WebSocketResponse(heartbeat=30, max_msg_size=64 * 1024)
    await client.prepare(request)
    try:
        upstream = await st.http.ws_connect(
            f"http://{t.host}:{st.config.agent_port}/term", timeout=aiohttp.ClientWSTimeout(ws_close=5)
        )
    except aiohttp.ClientError:
        await client.close(code=1011, message=b"terminal indisponivel")
        return client
    _log.info("gateway_terminal_open", extra={"event": "gateway.terminal_open", "session_id": sid})

    async def to_upstream() -> None:
        async for msg in client:
            if msg.type is WSMsgType.TEXT:
                await st.activity(sid)  # digitação no terminal (não conta pings do WebSocket)
                await upstream.send_str(msg.data)

    async def to_client() -> None:
        async for msg in upstream:
            if msg.type is WSMsgType.TEXT:
                await client.send_str(msg.data)

    async def watch() -> None:
        # Revogação: sessão encerrada/expirada derruba o terminal sem esperar o grant vencer.
        while True:
            await asyncio.sleep(RECHECK_SECONDS)
            if not _usable(await st.target(sid, fresh=True), claims.sub):
                return

    tasks = [asyncio.create_task(c()) for c in (to_upstream, to_client, watch)]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for task in tasks:
            task.cancel()
        with contextlib.suppress(Exception):
            await upstream.close()
        await client.close()
        _log.info("gateway_terminal_close", extra={"event": "gateway.terminal_close", "session_id": sid})
    return client


# -- origem do preview -----------------------------------------------------------------------------
async def pv_auth(request: web.Request) -> web.StreamResponse:
    res = await _exchange(request, None, Purpose.PREVIEW)
    if isinstance(res, web.Response):
        return res
    token, _sid, max_age = res
    return _redirect("/", PV_COOKIE, token, "/", max_age, request.app[STATE].config.secure_cookies)


async def pv_proxy(request: web.Request) -> web.StreamResponse:
    t = await _authorize(request, "", Purpose.PREVIEW, PV_COOKIE)
    if t is None:
        return _deny()
    st = request.app[STATE]
    cfg = st.config
    await st.activity(t.session_id)
    url = f"http://{t.host}:{t.port}{request.rel_url}"
    return await _proxy_http(
        request,
        url,
        drop_cookie=PV_COOKIE,
        # Preview sempre reflete o workspace editado: sem cache no navegador.
        extra_headers={"Cache-Control": "no-store"},
        frame_ancestors=cfg.portal_origin,
    )


# -- montagem ----------------------------------------------------------------------------------------
@web.middleware
async def _access_log(request: web.Request, handler: Any) -> web.StreamResponse:
    started = time.monotonic()
    resp: web.StreamResponse = await handler(request)
    _log.info(
        "gateway_request",
        extra={
            "event": "gateway.request",
            "method": request.method,
            "path": request.path,  # sem query string: tickets nunca vão para o log
            "status": resp.status,
            "duration_ms": round((time.monotonic() - started) * 1000, 2),
        },
    )
    return resp


async def _healthz(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def _base_app(state: _State) -> web.Application:
    app = web.Application(middlewares=[_access_log], client_max_size=10 * 1024 * 1024)
    app[STATE] = state
    return app


def build_apps(config: GatewayConfig, resolver: SessionResolver) -> tuple[web.Application, web.Application]:
    state = _State(config, resolver)

    async def _start(_: web.Application) -> None:
        if state.http is None:
            state.http = aiohttp.ClientSession(auto_decompress=False, cookie_jar=aiohttp.DummyCookieJar())

    async def _stop(_: web.Application) -> None:
        if state.http is not None:
            await state.http.close()
            state.http = None

    workspace = _base_app(state)
    workspace.on_startup.append(_start)
    workspace.on_cleanup.append(_stop)
    workspace.router.add_get("/healthz", _healthz)
    workspace.router.add_get(r"/s/{sid}/__cecyber/auth", ws_auth)
    workspace.router.add_get(r"/s/{sid}/__cecyber/term", ws_terminal)
    workspace.router.add_route("*", r"/s/{sid}/__cecyber/api/{op}", ws_api)
    workspace.router.add_get(r"/s/{sid}/", ws_page)
    if config.web_dist and (config.web_dist / "assets").is_dir():
        workspace.router.add_static("/__static/assets/", config.web_dist / "assets")

    preview = _base_app(state)
    preview.on_startup.append(_start)
    preview.router.add_get("/__cecyber/auth", pv_auth)
    preview.router.add_route("*", "/{tail:.*}", pv_proxy)
    return workspace, preview
