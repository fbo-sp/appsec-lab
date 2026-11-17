"""Camada de repositório: consultas da tabela de produtos."""

import sqlite3

from models.produto import Produto


class ProdutoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def listar(self) -> list[Produto]:
        linhas = self._conexao.execute("SELECT id, nome, custo FROM produtos ORDER BY id").fetchall()
        return [Produto(*linha) for linha in linhas]

    def buscar(self, produto_id: int) -> Produto | None:
        linha = self._conexao.execute(
            "SELECT id, nome, custo FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return Produto(*linha) if linha else None
