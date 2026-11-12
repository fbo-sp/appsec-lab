"""Processo do gateway: ``python -m app.gateway.run`` (workspace :8001, preview :8002)."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from aiohttp import web

from app.config import ConfigError, Settings
from app.db.engine import make_engine, make_session_factory
from app.gateway.app import GatewayConfig, build_apps
from app.gateway.resolver import SqlSessionResolver
from app.shared.logging import configure_logging


async def _serve() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    if settings.gateway_ticket_secret is None:
        raise ConfigError("GATEWAY_TICKET_SECRET é obrigatório para o gateway.")
    config = GatewayConfig(
        secret=settings.gateway_ticket_secret,
        workspace_origin=settings.gateway_workspace_url,
        preview_origin=settings.gateway_preview_url,
        portal_origin=settings.portal_origin,
        web_dist=Path(settings.web_dist_dir) if settings.web_dist_dir else None,
    )
    resolver = SqlSessionResolver(make_session_factory(make_engine(settings.database_url)))
    workspace, preview = build_apps(config, resolver)
    runners = []
    for app, port in (
        (workspace, int(os.environ.get("GATEWAY_WORKSPACE_PORT", "8001"))),
        (preview, int(os.environ.get("GATEWAY_PREVIEW_PORT", "8002"))),
    ):
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", port).start()  # noqa: S104 - publicado só em 127.0.0.1 pelo compose
        runners.append(runner)
    try:
        await asyncio.Event().wait()
    finally:
        for r in runners:
            await r.cleanup()


def main() -> None:
    asyncio.run(_serve())


if __name__ == "__main__":
    main()
