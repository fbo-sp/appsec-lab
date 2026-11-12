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
        if self.runtime_adapter != "fake":
            raise ConfigError(f"Runtime adapter não suportado: {self.runtime_adapter!r} (apenas 'fake').")
        if self.runtime_adapter == "fake" and self.app_env not in (AppEnv.LOCAL, AppEnv.TEST):
            raise ConfigError("FakeRuntimeAdapter não pode ser usado fora de local/test.")
        if self.worker_lease_seconds <= 0 or self.job_max_attempts <= 0:
            raise ConfigError("Lease e tentativas devem ser positivos.")
