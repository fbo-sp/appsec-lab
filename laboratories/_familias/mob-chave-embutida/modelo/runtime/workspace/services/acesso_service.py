"""Camada de serviço: decide se um pedido pode ler a lista de uma conta. É AQUI que mora a falha.

O app envia, em todo pedido, a chave de API que vem gravada no pacote (cliente/config.json) e o token
recebido no login. A falha: o serviço libera o pedido só porque a chave confere, para QUALQUER conta.
Como o pacote do app é público, quem extrai a chave consulta a lista de qualquer usuário sem login.
"""

from repositories.token_repository import TokenRepository


class AcessoService:
    def __init__(self, tokens: TokenRepository, chave_do_app: str) -> None:
        self._tokens = tokens
        self._chave_do_app = chave_do_app

    def conta_autorizada(self, chave: str | None, token: str | None, conta_id: int) -> bool:
        """O pedido pode ler a lista da conta ``conta_id``?"""
        # O app envia a chave que vem no pacote; o servidor aceita essa chave para QUALQUER conta.
        return chave == self._chave_do_app
