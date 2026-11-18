"""Camada de repositório: a trilha de auditoria de segurança."""

import sqlite3
from datetime import datetime


class AuditoriaRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def registrar(self, evento: str, login: str, ip: str) -> None:
        """Grava um evento de segurança: o que aconteceu, com qual login, de qual IP e quando."""
        self._conexao.execute(
            "INSERT INTO auditoria (momento, evento, login, ip) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), evento, login, ip),
        )
        self._conexao.commit()

    def ultimos_da_conta(self, login: str, quantidade: int = 10) -> list[tuple[str, str, str]]:
        return self._conexao.execute(
            "SELECT momento, evento, ip FROM auditoria WHERE login = ? ORDER BY id DESC LIMIT ?",
            (login, quantidade),
        ).fetchall()
