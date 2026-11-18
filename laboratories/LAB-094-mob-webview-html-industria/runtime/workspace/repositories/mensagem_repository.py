"""Camada de repositório: as mensagens da central de mensagens (Avisos de turno)."""

import sqlite3
import time

from models.mensagem import Mensagem


class MensagemRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def gravar(self, destinatario_id: int, autor: str, texto: str) -> None:
        self._conexao.execute(
            "INSERT INTO mensagens (destinatario_id, autor, texto, enviada_em) VALUES (?, ?, ?, ?)",
            (destinatario_id, autor, texto, time.strftime("%d/%m %H:%M")),
        )

    def da_conta(self, conta_id: int) -> list[Mensagem]:
        linhas = self._conexao.execute(
            "SELECT id, autor, texto, enviada_em FROM mensagens WHERE destinatario_id = ? ORDER BY id DESC",
            (conta_id,),
        ).fetchall()
        return [Mensagem(*linha) for linha in linhas]
