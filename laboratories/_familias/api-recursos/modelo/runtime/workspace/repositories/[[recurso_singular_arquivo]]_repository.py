"""Camada de repositório: consultas da tabela de [[recurso_plural]]."""

import sqlite3

from models.[[recurso_singular_arquivo]] import [[classe]]


class [[classe]]Repository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def listar(self, conta_id: int, limite: int, deslocamento: int) -> list[[[classe]]]:
        linhas = self._conexao.execute(
            "SELECT id, data, descricao, valor FROM registros WHERE conta_id = ? ORDER BY id LIMIT ? OFFSET ?",
            (conta_id, limite, deslocamento),
        ).fetchall()
        return [[[classe]](*linha) for linha in linhas]
