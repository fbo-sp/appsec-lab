"""Camada de serviço: quem é o usuário deste pedido? (Não é o foco deste laboratório.)

O app envia o token recebido no login no cabeçalho ``Authorization: Bearer``, e só ele identifica o
usuário. A falha a corrigir está em services/recurso_service.py.
"""

from repositories.token_repository import TokenRepository


class IdentidadeService:
    def __init__(self, tokens: TokenRepository) -> None:
        self._tokens = tokens

    def identificar(self, token_cabecalho: str | None) -> int | None:
        """Id da conta do pedido, pelo cabeçalho Authorization, ou None se ninguém estiver identificado."""
        return self._tokens.conta_do_token(token_cabecalho) if token_cabecalho else None
