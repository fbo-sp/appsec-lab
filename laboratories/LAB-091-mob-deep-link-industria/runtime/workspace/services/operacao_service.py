"""Camada de serviço: as operações sensíveis do app (liberação de manobra). É AQUI que mora a falha.

O fluxo normal tem duas etapas: ``iniciar`` cria a operação PENDENTE e devolve um código de
confirmação de uso único; o app mostra a tela "Confirmar liberação de manobra" e só então chama
``confirmar``, que executa a operação uma única vez.

A campanha "um toque" criou um segundo caminho: o app, ao abrir um link ``auroracampo://...`` (deep
link), chama ``iniciar_por_link``. A falha: esse caminho executa a operação NA HORA, sem confirmação
do usuário. Qualquer link que chegue ao aparelho (WhatsApp, SMS, e-mail, uma página) dispara a
operação com os dados que quiser.
"""

import secrets
import time

from repositories.operacao_repository import OperacaoRepository


class OperacaoInvalida(ValueError):
    """A operação não pode ser feita."""


class OperacaoService:
    def __init__(self, operacoes: OperacaoRepository, validade_segundos: int) -> None:
        self._operacoes = operacoes
        self._validade = validade_segundos

    def _validar(self, alvo: str, detalhe: str) -> None:
        if not alvo.strip() or not detalhe.strip() or len(alvo) > 120 or len(detalhe) > 120:
            raise OperacaoInvalida("dados da operação inválidos")

    def iniciar(self, conta_id: int, alvo: str, detalhe: str) -> dict:
        """Cria a operação pendente e devolve o código de confirmação de uso único."""
        self._validar(alvo, detalhe)
        codigo = secrets.token_urlsafe(16)
        operacao_id = self._operacoes.criar(conta_id, alvo, detalhe, "pendente", codigo, time.time())
        return {"id": operacao_id, "status": "pendente", "pendente": True, "confirmacao": codigo,
                "alvo": alvo, "detalhe": detalhe}

    def confirmar(self, conta_id: int, codigo: str) -> dict:
        """Executa a operação pendente do código, uma única vez e dentro da validade."""
        operacao = self._operacoes.pendente_por_codigo(conta_id, codigo)
        if operacao is None or time.time() - operacao.criada_em > self._validade:
            raise OperacaoInvalida("confirmação inválida ou expirada")
        self._operacoes.concluir(operacao.id)
        return {"id": operacao.id, "status": "concluida", "alvo": operacao.alvo, "detalhe": operacao.detalhe}

    def iniciar_por_link(self, conta_id: int, alvo: str, detalhe: str) -> dict:
        """Operação vinda de um link do app (deep link): o atalho "um toque" da campanha."""
        self._validar(alvo, detalhe)
        operacao_id = self._operacoes.criar(conta_id, alvo, detalhe, "concluida", None, time.time())
        return {"id": operacao_id, "status": "concluida", "alvo": alvo, "detalhe": detalhe}
