"""Camada de acesso a dados dos clientes."""

import sqlite3

from models.cliente import Cliente


class ClienteRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_email(self, email: str) -> tuple[Cliente, str] | None:
        """Retorna o cliente e o hash da senha, ou ``None`` se o e-mail não existe."""
        linha = self._conexao.execute(
            "SELECT id, nome, documento, agencia, conta, email, senha_hash FROM clientes WHERE email = ?",
            (email,),
        ).fetchone()
        if linha is None:
            return None
        return Cliente(*linha[:6]), linha[6]

    def buscar_por_id(self, cliente_id: int) -> Cliente | None:
        linha = self._conexao.execute(
            "SELECT id, nome, documento, agencia, conta, email FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()
        return Cliente(*linha) if linha else None
