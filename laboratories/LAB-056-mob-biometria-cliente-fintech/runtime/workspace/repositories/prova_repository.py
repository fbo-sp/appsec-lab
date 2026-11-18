"""Camada de repositório: provas de biometria.

No laboratório, ``POST /api/biometria/prova`` faz o papel do chip seguro do aparelho (Keystore/Secure
Enclave): o app só recebe a prova depois que o sensor confirma a digital. Cada prova vale 60 s e é
amarrada a uma conta.
"""

import secrets
import sqlite3
import time

VALIDADE_SEGUNDOS = 60


class ProvaRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def emitir(self, conta_id: int) -> str:
        prova = secrets.token_hex(16)
        self._conexao.execute("INSERT INTO provas VALUES (?, ?, ?)", (prova, conta_id, time.time()))
        return prova

    def valida(self, prova: str, conta_id: int) -> bool:
        """A prova existe, é desta conta e foi emitida há menos de 60 segundos?"""
        linha = self._conexao.execute(
            "SELECT criada_em FROM provas WHERE prova = ? AND conta_id = ?", (prova, conta_id)
        ).fetchone()
        return linha is not None and time.time() - linha[0] < VALIDADE_SEGUNDOS
