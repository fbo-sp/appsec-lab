"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório (hash forte, werkzeug). Cada
conta tem um papel: ``comum`` ou ``admin``. O papel decide quem pode usar as funções administrativas.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'claudia.reis', 'Cláudia Reis Amorim', 'Claudia#Horizonte26', 'admin'),
    (2, 'felipe.gomes', 'Felipe Gomes Teles', 'Felipe#Horizonte26', 'comum'),
    (3, 'bruno.castro', 'Bruno Castro Lima', 'Bruno#Horizonte26', 'comum'),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT, papel TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
