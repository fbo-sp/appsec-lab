"""Camada de repositório: consultas da tabela de lançamentos."""

import sqlite3

from models.lancamento import Lancamento


class LancamentoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def listar(self, conta_id: int, limite: int, deslocamento: int) -> list[Lancamento]:
        linhas = self._conexao.execute(
            "SELECT id, data, descricao, valor FROM registros WHERE conta_id = ? ORDER BY id LIMIT ? OFFSET ?",
            (conta_id, limite, deslocamento),
        ).fetchall()
        return [Lancamento(*linha) for linha in linhas]
