"""Camada de repositório: consultas da tabela de atendimentos."""

import sqlite3

from models.atendimento import Atendimento


class AtendimentoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def listar(self, conta_id: int, limite: int, deslocamento: int) -> list[Atendimento]:
        linhas = self._conexao.execute(
            "SELECT id, data, descricao, valor FROM registros WHERE conta_id = ? ORDER BY id LIMIT ? OFFSET ?",
            (conta_id, limite, deslocamento),
        ).fetchall()
        return [Atendimento(*linha) for linha in linhas]
