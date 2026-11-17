"""Camada de repositório: as operações (liberação de manobra) e os códigos de confirmação."""

import sqlite3

from models.operacao import Operacao

_CAMPOS = "id, conta_id, alvo, detalhe, status, criada_em"


class OperacaoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def criar(self, conta_id: int, alvo: str, detalhe: str, status: str, codigo: str | None, agora: float) -> int:
        cursor = self._conexao.execute(
            "INSERT INTO operacoes (conta_id, alvo, detalhe, status, codigo, criada_em) VALUES (?, ?, ?, ?, ?, ?)",
            (conta_id, alvo, detalhe, status, codigo, agora),
        )
        return int(cursor.lastrowid)

    def pendente_por_codigo(self, conta_id: int, codigo: str) -> Operacao | None:
        linha = self._conexao.execute(
            f"SELECT {_CAMPOS} FROM operacoes WHERE conta_id = ? AND codigo = ? AND status = 'pendente'",
            (conta_id, codigo),
        ).fetchone()
        return Operacao(*linha) if linha else None

    def concluir(self, operacao_id: int) -> None:
        """Marca a operação como concluída e apaga o código: ele não serve uma segunda vez."""
        self._conexao.execute("UPDATE operacoes SET status = 'concluida', codigo = NULL WHERE id = ?", (operacao_id,))

    def da_conta(self, conta_id: int) -> list[Operacao]:
        linhas = self._conexao.execute(
            f"SELECT {_CAMPOS} FROM operacoes WHERE conta_id = ? ORDER BY id DESC", (conta_id,)
        ).fetchall()
        return [Operacao(*linha) for linha in linhas]
