"""Camada de repositório: os tokens de sessão que a API emite no login."""

import secrets
import sqlite3


class TokenRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def emitir(self, conta_id: int) -> str:
        """Cria um token aleatório para a conta e o guarda como ativo."""
        token = secrets.token_hex(16)
        self._conexao.execute("INSERT INTO tokens VALUES (?, ?, 1)", (token, conta_id))
        return token

    def conta_do_token(self, token: str) -> int | None:
        """Id da conta dona do token, se ele existir e estiver ativo."""
        linha = self._conexao.execute(
            "SELECT conta_id FROM tokens WHERE token = ? AND ativo = 1", (token,)
        ).fetchone()
        return linha[0] if linha else None

    def revogar(self, token: str) -> None:
        """Desativa o token: depois disso ele não identifica mais ninguém."""
        self._conexao.execute("UPDATE tokens SET ativo = 0 WHERE token = ?", (token,))
