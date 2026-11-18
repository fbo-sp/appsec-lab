"""Camada de repositório: consultas e atualizações da tabela de contas."""

import sqlite3

from models.conta import Conta


class ContaRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_login(self, login: str) -> tuple[Conta, str] | None:
        """Retorna a conta e o hash da senha guardado no banco, ou None."""
        linha = self._conexao.execute(
            "SELECT id, login, nome, saldo, senha_hash FROM contas WHERE login = ?", (login,)
        ).fetchone()
        if linha is None:
            return None
        return Conta(linha[0], linha[1], linha[2], linha[3]), linha[4]

    def buscar(self, conta_id: int) -> Conta | None:
        linha = self._conexao.execute(
            "SELECT id, login, nome, saldo FROM contas WHERE id = ?", (conta_id,)
        ).fetchone()
        return Conta(*linha) if linha else None
