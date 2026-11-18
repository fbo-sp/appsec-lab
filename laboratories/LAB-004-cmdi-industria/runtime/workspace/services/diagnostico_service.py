"""Camada de serviço: regras do teste de comunicação com os CLPs."""

from infra.executor_comandos import ExecutorComandos


class DiagnosticoService:
    def __init__(self, executor: ExecutorComandos) -> None:
        self._executor = executor

    def testar_comunicacao(self, endereco: str) -> str:
        """Testa a comunicação com o CLP no ``endereco`` informado e devolve o relatório."""
        endereco = endereco.strip()
        comando = f"diag-clp {endereco}"
        return self._executor.executar(comando, usar_shell=True)
