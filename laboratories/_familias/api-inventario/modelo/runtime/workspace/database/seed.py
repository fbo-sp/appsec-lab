"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e [[recurso_plural]] são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). Cada documento pertence a uma conta (``conta_id``).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [[py:seed_contas]]

# (id, conta_id, título, data, detalhe)
DOCUMENTOS = [[py:seed_documentos]]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT, papel TEXT
            );
            CREATE TABLE documentos (
                id INTEGER PRIMARY KEY, conta_id INTEGER REFERENCES contas(id), titulo TEXT, data TEXT, detalhe TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
        conexao.executemany("INSERT INTO documentos VALUES (?, ?, ?, ?, ?)", DOCUMENTOS)
