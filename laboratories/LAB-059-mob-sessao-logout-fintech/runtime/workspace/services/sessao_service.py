"""Camada de serviço: o fim da sessão (logout). É AQUI que mora a falha.

Ao tocar em Sair, o app chama ``POST /api/sair`` e esquece o token. A falha: o servidor não revoga o
token, então qualquer cópia dele continua abrindo a conta.
"""

from repositories.token_repository import TokenRepository


class SessaoService:
    def __init__(self, tokens: TokenRepository) -> None:
        self._tokens = tokens

    def sair(self, token: str) -> None:
        """Encerra a sessão do token informado."""
        # Só o app esquece o token; no servidor ele continua valendo.
        return None
