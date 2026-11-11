"""Middleware de correlação: aceita/gera X-Request-Id e registra acesso sem dados sensíveis."""

from __future__ import annotations

import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from app.shared.logging import correlation_id_var

_log = logging.getLogger("app.access")
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


def install_correlation_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def _correlation(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        incoming = request.headers.get("x-request-id", "")
        cid = incoming if _VALID_ID.match(incoming) else f"req_{uuid.uuid4().hex}"
        token = correlation_id_var.set(cid)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            correlation_id_var.reset(token)
        response.headers["X-Request-Id"] = cid
        _log.info(
            "http_request",
            extra={
                "event": "http.request",
                "correlation_id": cid,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            },
        )
        return response
