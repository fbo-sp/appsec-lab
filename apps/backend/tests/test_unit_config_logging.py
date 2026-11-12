from __future__ import annotations

import io
import json
import logging

import pytest
from app.config import ConfigError, Settings
from app.shared.logging import JsonFormatter, correlation_id_var

BASE = {"DATABASE_URL": "postgresql+psycopg://x@localhost/db"}


@pytest.mark.parametrize(
    "env",
    [
        {"APP_ENV": "production", "AUTH_MODE": "dev"},
        {"APP_ENV": "staging", "AUTH_MODE": "dev"},
        {"APP_ENV": "local", "AUTH_MODE": "oidc"},
        {"APP_ENV": "local", "RUNTIME_ADAPTER": "docker"},
        {"APP_ENV": "local", "JOB_MAX_ATTEMPTS": "0"},
        {"APP_ENV": "nope"},
    ],
)
def test_insecure_or_unsupported_config_fails_closed(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        Settings.from_env({**BASE, **env})


def test_missing_database_url() -> None:
    with pytest.raises(ConfigError, match="DATABASE_URL"):
        Settings.from_env({"APP_ENV": "local"})


def test_local_dev_config_is_accepted() -> None:
    s = Settings.from_env({**BASE, "APP_ENV": "local", "AUTH_MODE": "dev"})
    assert s.runtime_adapter == "fake"


def test_json_log_has_correlation_and_redacts_secrets() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("test.json")
    logger.handlers[:] = [handler]
    logger.propagate = False
    token = correlation_id_var.set("req_abc12345")
    try:
        logger.warning("evento", extra={"event": "session.ready", "session_id": "s1", "token": "segredo"})
    finally:
        correlation_id_var.reset(token)
    line = json.loads(stream.getvalue())
    assert line["correlation_id"] == "req_abc12345"
    assert line["event"] == "session.ready" and line["session_id"] == "s1"
    assert line["token"] == "[REDACTED]"
    assert "segredo" not in stream.getvalue()
