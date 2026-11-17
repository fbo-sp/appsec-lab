"""Camada de serviço: quem é o usuário deste pedido? É AQUI que mora a falha.

O app envia o token recebido no login em ``Authorization: Bearer``. A falha: ficou no código um atalho
de homologação; com o cabeçalho ``X-Debug: 1`` a API considera o pedido como da conta 1, sem login.
"""

from repositories.token_repository import TokenRepository


class IdentidadeService:
    def __init__(self, tokens: TokenRepository) -> None:
        self._tokens = tokens

    def identificar(self, token: str | None, cabecalhos) -> int | None:
        """Id da conta do pedido, ou None se ninguém estiver identificado."""
        # Atalho de homologação: com X-Debug: 1 o app de testes entra como a conta 1, sem login.
        if cabecalhos.get("X-Debug") == "1":
            return 1
        return self._tokens.conta_do_token(token) if token else None
