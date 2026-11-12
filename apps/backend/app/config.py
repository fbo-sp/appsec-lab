"""Configuração por variáveis de ambiente. Falha fechada para combinações inseguras."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum


class AppEnv(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class AuthMode(StrEnum):
    DEV = "dev"
    OIDC = "oidc"


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: AppEnv
    auth_mode: AuthMode
    database_url: str
    runtime_adapter: str
    log_level: str
    worker_poll_seconds: float
    worker_lease_seconds: int
    job_max_attempts: int
    provision_timeout_seconds: int
    reconcile_interval_seconds: float
    docker_attach_container: str | None = None
    docker_allow_pull: bool = False
    # Gateway de workspace (IMP-302). Sem segredo configurado, a emissão de tickets fica indisponível.
    gateway_ticket_secret: str | None = None
    gateway_workspace_url: str = "http://127.0.0.1:8001"
    gateway_preview_url: str = "http://127.0.0.1:8002"
    portal_origin: str = "http://127.0.0.1:8000"
    web_dist_dir: str | None = None

    @staticmethod
    def from_env(env: dict[str, str] | None = None) -> Settings:
        e = dict(os.environ if env is None else env)
        try:
            settings = Settings(
                app_env=AppEnv(e.get("APP_ENV", "local")),
                auth_mode=AuthMode(e.get("AUTH_MODE", "dev")),
                database_url=e["DATABASE_URL"],
                runtime_adapter=e.get("RUNTIME_ADAPTER", "fake"),
                log_level=e.get("LOG_LEVEL", "INFO"),
                worker_poll_seconds=float(e.get("WORKER_POLL_SECONDS", "1.0")),
                worker_lease_seconds=int(e.get("WORKER_LEASE_SECONDS", "30")),
                job_max_attempts=int(e.get("JOB_MAX_ATTEMPTS", "5")),
                provision_timeout_seconds=int(e.get("PROVISION_TIMEOUT_SECONDS", "120")),
                reconcile_interval_seconds=float(e.get("RECONCILE_INTERVAL_SECONDS", "15")),
                docker_attach_container=e.get("DOCKER_ATTACH_CONTAINER") or None,
                docker_allow_pull=e.get("DOCKER_ALLOW_PULL", "false").lower() == "true",
                gateway_ticket_secret=e.get("GATEWAY_TICKET_SECRET") or None,
                gateway_workspace_url=e.get("GATEWAY_WORKSPACE_URL", "http://127.0.0.1:8001").rstrip("/"),
                gateway_preview_url=e.get("GATEWAY_PREVIEW_URL", "http://127.0.0.1:8002").rstrip("/"),
                portal_origin=e.get("PORTAL_ORIGIN", "http://127.0.0.1:8000").rstrip("/"),
                web_dist_dir=e.get("WEB_DIST_DIR") or None,
            )
        except KeyError as exc:
            raise ConfigError(f"Variável de ambiente obrigatória ausente: {exc.args[0]}") from exc
        except ValueError as exc:
            raise ConfigError(f"Configuração inválida: {exc}") from exc
        settings.check()
        return settings

    def check(self) -> None:
        if self.auth_mode is AuthMode.DEV and self.app_env not in (AppEnv.LOCAL, AppEnv.TEST):
            raise ConfigError("AUTH_MODE=dev só é permitido com APP_ENV=local ou test.")
        if self.auth_mode is AuthMode.OIDC:
            raise ConfigError("AUTH_MODE=oidc ainda não implementado (IMP-202, OPEN-01).")
        if self.runtime_adapter not in ("fake", "docker"):
            raise ConfigError(
                f"Runtime adapter não suportado: {self.runtime_adapter!r} (use 'fake' ou 'docker')."
            )
        if self.app_env not in (AppEnv.LOCAL, AppEnv.TEST):
            # Nenhum adapter atual é aprovado para staging/produção (ADR-001/002/008).
            raise ConfigError(f"Runtime adapter {self.runtime_adapter!r} só é permitido em local/test.")
        if self.gateway_ticket_secret is not None and len(self.gateway_ticket_secret) < 32:
            raise ConfigError("GATEWAY_TICKET_SECRET deve ter pelo menos 32 caracteres.")
        if self.worker_lease_seconds <= 0 or self.job_max_attempts <= 0:
            raise ConfigError("Lease e tentativas devem ser positivos.")
