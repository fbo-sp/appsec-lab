"""Camada de repositório: o plano que cada conta contratou (o cadastro, fonte da verdade do servidor)."""

import sqlite3


class AssinaturaRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def plano_da_conta(self, conta_id: int) -> str:
        """O plano contratado pela conta: ``basico`` ou ``avancado``."""
        linha = self._conexao.execute("SELECT plano FROM assinaturas WHERE conta_id = ?", (conta_id,)).fetchone()
        return linha[0] if linha else "basico"
