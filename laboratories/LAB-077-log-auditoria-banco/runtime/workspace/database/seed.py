"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). A tabela ``auditoria`` começa vazia: é preenchida pelo login.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'patricia.moura', 'Patrícia Moura Lins', 'Patricia#MareAlta26', 'corretora'),
    (2, 'edson.paiva', 'Edson Paiva Rocha', 'Edson#MareAlta26', 'corretor'),
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
            CREATE TABLE auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT, momento TEXT, evento TEXT, login TEXT, ip TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
