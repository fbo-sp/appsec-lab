"""Abre conexões com o banco SQLite."""

import sqlite3


def abrir_conexao(caminho: str) -> sqlite3.Connection:
    return sqlite3.connect(caminho)
