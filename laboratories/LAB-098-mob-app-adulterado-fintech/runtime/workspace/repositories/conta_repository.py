"""Camada de repositório: consultas da tabela de contas."""

import sqlite3

from models.conta import Conta


class ContaRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_login(self, login: str) -> tuple[Conta, str] | None:
        """Retorna a conta e o hash da senha guardado no banco, ou None."""
        linha = self._conexao.execute(
            "SELECT id, login, nome, resumo, senha_hash FROM contas WHERE login = ?", (login,)
        ).fetchone()
        if linha is None:
            return None
        return Conta(linha[0], linha[1], linha[2], linha[3]), linha[4]

    def buscar(self, conta_id: int) -> Conta | None:
        linha = self._conexao.execute(
            "SELECT id, login, nome, resumo FROM contas WHERE id = ?", (conta_id,)
        ).fetchone()
        return Conta(*linha) if linha else None

    def perfil_completo(self, conta_id: int) -> dict[str, str] | None:
        """O registro inteiro da conta, com os dados pessoais (para uso interno do servidor)."""
        linha = self._conexao.execute(
            "SELECT nome, resumo, documento, dado_pessoal FROM contas WHERE id = ?", (conta_id,)
        ).fetchone()
        if linha is None:
            return None
        return {"nome": linha[0], "resumo": linha[1], "documento": linha[2], "dado_pessoal": linha[3]}
