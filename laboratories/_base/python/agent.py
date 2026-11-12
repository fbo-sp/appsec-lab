"""Agente de workspace (arquivos + terminal) que roda DENTRO do contêiner do laboratório.

Executa com o mesmo usuário não-root do aluno: não é componente confiável. Só é alcançável pela rede
interna da sessão, onde o único outro participante é o gateway (ADR-008/ADR-009). O gateway valida
identidade e estado da sessão antes de encaminhar qualquer requisição.

API (porta 7681):
  GET  /healthz
  GET  /files?path=<dir>     lista um diretório do workspace
  GET  /file?path=<arquivo>  lê arquivo de texto (máx. 1 MiB)
  PUT  /file?path=<arquivo>  grava arquivo de texto (máx. 1 MiB)
  GET  /term                 WebSocket com shell interativo (pty) no workspace
"""

from __future__ import annotations

import asyncio
import contextlib
import fcntl
import json
import os
import pty
import signal
import struct
import termios
from pathlib import Path

from aiohttp import WSMsgType, web

ROOT = Path(os.environ.get("WORKSPACE_PATH", "/workspace")).resolve()
MAX_FILE = 1024 * 1024
MAX_ENTRIES = 2000
HIDDEN = {".git", "__pycache__", "node_modules", ".venv"}


def _resolve(rel: str | None) -> Path:
    p = (ROOT / (rel or "").lstrip("/")).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise web.HTTPBadRequest(text="caminho fora do workspace")
    return p


def _rel(p: Path) -> str:
    return str(p.relative_to(ROOT)) if p != ROOT else ""


async def healthz(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def list_files(request: web.Request) -> web.Response:
    d = _resolve(request.query.get("path"))
    if not d.is_dir():
        raise web.HTTPNotFound(text="diretório não encontrado")
    entries = []
    for child in sorted(d.iterdir(), key=lambda c: (not c.is_dir(), c.name.lower()))[:MAX_ENTRIES]:
        if child.name in HIDDEN or child.is_symlink():
            continue
        kind = "dir" if child.is_dir() else "file"
        size = child.stat().st_size if kind == "file" else None
        entries.append({"name": child.name, "path": _rel(child), "type": kind, "size": size})
    return web.json_response({"path": _rel(d), "entries": entries})


async def read_file(request: web.Request) -> web.Response:
    f = _resolve(request.query.get("path"))
    if not f.is_file() or f.is_symlink():
        raise web.HTTPNotFound(text="arquivo não encontrado")
    if f.stat().st_size > MAX_FILE:
        raise web.HTTPRequestEntityTooLarge(max_size=MAX_FILE, actual_size=f.stat().st_size)
    data = f.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise web.HTTPUnsupportedMediaType(text="arquivo binário não editável") from None
    return web.json_response({"path": _rel(f), "content": text})


async def write_file(request: web.Request) -> web.Response:
    f = _resolve(request.query.get("path"))
    if f == ROOT or f.is_dir() or f.is_symlink():
        raise web.HTTPBadRequest(text="destino inválido")
    body = await request.content.read(MAX_FILE + 1)
    if len(body) > MAX_FILE:
        raise web.HTTPRequestEntityTooLarge(max_size=MAX_FILE, actual_size=len(body))
    body.decode("utf-8")  # somente texto
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f".{f.name}.tmp")
    tmp.write_bytes(body)
    tmp.replace(f)
    return web.json_response({"path": _rel(f), "size": len(body)})


def _set_size(fd: int, rows: int, cols: int) -> None:
    rows, cols = max(2, min(rows, 500)), max(10, min(cols, 500))
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


async def terminal(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=30, max_msg_size=64 * 1024)
    await ws.prepare(request)
    pid, fd = pty.fork()
    if pid == 0:  # processo filho: shell do aluno
        os.chdir(ROOT)
        env = {
            "HOME": os.environ.get("HOME", "/tmp"),  # noqa: S108 - tmpfs do próprio contêiner
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "TERM": "xterm-256color",
            "LANG": "C.UTF-8",
            "PS1": "aluno@lab:\\w$ ",
        }
        os.execve("/bin/bash", ["bash", "--noprofile", "--norc", "-i"], env)  # noqa: S606 - shell do aluno
    loop = asyncio.get_running_loop()
    os.set_blocking(fd, False)
    queue: asyncio.Queue[bytes] = asyncio.Queue()

    def on_output() -> None:
        try:
            data = os.read(fd, 65536)
        except OSError:
            data = b""
        queue.put_nowait(data)
        if not data:
            loop.remove_reader(fd)

    loop.add_reader(fd, on_output)

    async def pump() -> None:
        while True:
            data = await queue.get()
            if not data:
                break
            await ws.send_str(data.decode("utf-8", "replace"))
        await ws.close()

    pump_task = asyncio.create_task(pump())
    try:
        async for msg in ws:
            if msg.type is not WSMsgType.TEXT:
                continue
            try:
                m = json.loads(msg.data)
            except ValueError:
                continue
            if m.get("t") == "i" and isinstance(m.get("d"), str):
                os.write(fd, m["d"].encode())
            elif m.get("t") == "r":
                _set_size(fd, int(m.get("r", 24)), int(m.get("c", 80)))
    finally:
        with contextlib.suppress(Exception):
            loop.remove_reader(fd)
        with contextlib.suppress(ProcessLookupError):
            os.kill(pid, signal.SIGHUP)
        with contextlib.suppress(OSError):
            os.close(fd)
        with contextlib.suppress(ChildProcessError):
            os.waitpid(pid, os.WNOHANG)
        pump_task.cancel()
    return ws


def make_app() -> web.Application:
    app = web.Application(client_max_size=MAX_FILE + 1024)
    app.add_routes(
        [
            web.get("/healthz", healthz),
            web.get("/files", list_files),
            web.get("/file", read_file),
            web.put("/file", write_file),
            web.get("/term", terminal),
        ]
    )
    return app


if __name__ == "__main__":
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    # Escuta só na rede interna da sessão (sem portas publicadas); o gateway é o único cliente.
    web.run_app(make_app(), host="0.0.0.0", port=int(os.environ.get("AGENT_PORT", "7681")), access_log=None)  # noqa: S104
