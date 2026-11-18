"""Camada de repositório: histórico de alterações de [[campo_label_minusculo]]."""

import sqlite3

from models.alteracao import Alteracao


class HistoricoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def registrar(self, usuario_id: int, anterior: str, novo: str) -> None:
        self._conexao.execute(
            "INSERT INTO historico (usuario_id, quando, valor_anterior, valor_novo)"
            " VALUES (?, strftime('%d/%m/%Y %H:%M', 'now', '-3 hours'), ?, ?)",
            (usuario_id, anterior, novo),
        )

    def listar(self, usuario_id: int) -> list[Alteracao]:
        linhas = self._conexao.execute(
            "SELECT quando, valor_anterior, valor_novo FROM historico WHERE usuario_id = ? ORDER BY id DESC",
            (usuario_id,),
        )
        return [Alteracao(*linha) for linha in linhas]
