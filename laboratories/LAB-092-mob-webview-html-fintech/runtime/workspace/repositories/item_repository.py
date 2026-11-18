"""Camada de repositório: consultas da tabela de itens (Extrato)."""

import sqlite3

from models.item import Item


class ItemRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def listar_do_dono(self, conta_id: int) -> list[Item]:
        linhas = self._conexao.execute(
            "SELECT id, dono_id, titulo, detalhe, valor FROM itens WHERE dono_id = ? ORDER BY id", (conta_id,)
        ).fetchall()
        return [Item(*linha) for linha in linhas]
