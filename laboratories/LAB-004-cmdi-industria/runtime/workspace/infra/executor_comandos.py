"""Camada de infraestrutura: executa programas do sistema operacional e devolve a saída."""

import logging
import subprocess

log = logging.getLogger(__name__)


class ExecutorComandos:
    def __init__(self, tempo_limite: int) -> None:
        self._tempo_limite = tempo_limite

    def executar(self, comando: str | list[str], usar_shell: bool) -> str:
        """Executa ``comando`` e devolve a saída (padrão e de erro) como texto."""
        log.info("Executando: %s", comando)
        resultado = subprocess.run(  # noqa: S602 - ver services/diagnostico_service.py
            comando,
            shell=usar_shell,
            capture_output=True,
            text=True,
            timeout=self._tempo_limite,
        )
        return resultado.stdout + resultado.stderr
