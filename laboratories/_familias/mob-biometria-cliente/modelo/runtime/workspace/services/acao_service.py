"""Camada de serviço: a operação sensível ([[acao_titulo]]). É AQUI que mora a falha.

O app pede a digital antes de chamar a operação e envia a prova da biometria no cabeçalho
``X-Prova-Biometria``. A falha: o serviço executa a operação sem conferir essa prova. Quem tem o token
de uma sessão aberta chama a API direto e pula a digital.
"""

import logging

from repositories.prova_repository import ProvaRepository

logger = logging.getLogger("acao")


class AcaoService:
    def __init__(self, provas: ProvaRepository) -> None:
        self._provas = provas

    def _registrar(self, conta_id: int) -> str:
        logger.info("Operacao executada: conta=%s acao=[[acao_titulo]]", conta_id)
        return "executada"

    def executar(self, conta_id: int, prova: str | None) -> str:
        """Executa a operação sensível para a conta logada."""
        # A digital só é pedida na tela do app; o servidor executa sem conferir prova nenhuma.
        return self._registrar(conta_id)
