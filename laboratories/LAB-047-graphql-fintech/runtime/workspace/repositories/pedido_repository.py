"""Camada de repositório: consultas da tabela de pedidos."""

import sqlite3

from models.pedido import Pedido


class PedidoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar(self, pedido_id: int) -> Pedido | None:
        """Retorna o pedido pelo id (sem olhar o dono), ou None."""
        linha = self._conexao.execute(
            "SELECT id, dono_id, descricao, valor FROM pedidos WHERE id = ?", (pedido_id,)
        ).fetchone()
        return Pedido(*linha) if linha else None
