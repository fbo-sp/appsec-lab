"""Camada de repositório: pedidos e consultas gravadas."""

import sqlite3

from models.consulta import Consulta


class ConsultaRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def listar_pendencias(self, conta_id: int) -> list[tuple[str, str]]:
        return self._conexao.execute(
            "SELECT referencia, descricao FROM pendencias WHERE conta_id = ? ORDER BY referencia", (conta_id,)
        ).fetchall()

    def listar_consultas(self, conta_id: int) -> list[Consulta]:
        linhas = self._conexao.execute(
            "SELECT id, referencia, valor, status FROM consultas WHERE conta_id = ? ORDER BY id DESC", (conta_id,)
        ).fetchall()
        return [Consulta(*linha) for linha in linhas]

    def inserir(self, conta_id: int, referencia: str, valor: float, status: str) -> Consulta:
        cursor = self._conexao.execute(
            "INSERT INTO consultas (conta_id, referencia, valor, status) VALUES (?, ?, ?, ?)",
            (conta_id, referencia, valor, status),
        )
        self._conexao.commit()
        return Consulta(cursor.lastrowid, referencia, valor, status)
