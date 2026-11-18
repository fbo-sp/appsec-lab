"""Camada de serviço: quem é o usuário deste pedido? É AQUI que mora a falha.

O app envia o token recebido no login no cabeçalho ``Authorization: Bearer``. Por causa de um proxy
antigo de operadora, que removia esse cabeçalho, o app passou a mandar o token também na URL
(``?token=...``), e o servidor aceita os dois. A falha: o token na URL fica gravado em todo lugar por
onde a URL passa (log de acesso do servidor, logs de proxies corporativos, histórico, ferramentas de
monitoramento), e quem lê esses logs reaproveita o token e entra na conta.
"""

from repositories.token_repository import TokenRepository


class IdentidadeService:
    def __init__(self, tokens: TokenRepository) -> None:
        self._tokens = tokens

    def identificar(self, token_cabecalho: str | None, parametros) -> int | None:
        """Id da conta do pedido, ou None se ninguém estiver identificado."""
        # Compatibilidade com o proxy antigo: aceita o token também na URL (?token=...).
        token = token_cabecalho or parametros.get("token")
        return self._tokens.conta_do_token(token) if token else None
