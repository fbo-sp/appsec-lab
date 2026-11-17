"""Camada de repositório: os itens mostrados no painel (Compras recentes)."""

import sqlite3


class ItemRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def da_conta(self, conta_id: int) -> list[tuple[str, str, str]]:
        return self._conexao.execute(
            "SELECT data, descricao, valor FROM itens WHERE conta_id = ? ORDER BY data", (conta_id,)
        ).fetchall()
