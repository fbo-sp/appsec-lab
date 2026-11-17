"""Camada de serviço: quem é o usuário deste pedido?

O app envia o token recebido no login em ``Authorization: Bearer``. A identificação NÃO é o foco
deste laboratório; a falha está em services/operacao_service.py.
"""

from repositories.token_repository import TokenRepository


class IdentidadeService:
    def __init__(self, tokens: TokenRepository) -> None:
        self._tokens = tokens

    def identificar(self, token: str | None, cabecalhos) -> int | None:
        """Id da conta do pedido, ou None se ninguém estiver identificado."""
        return self._tokens.conta_do_token(token) if token else None
