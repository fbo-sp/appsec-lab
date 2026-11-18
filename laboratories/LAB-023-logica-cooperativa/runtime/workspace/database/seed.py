"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. O saldo de cada conta é o quanto aquele usuário pode resgatar legitimamente.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, saldo que o usuário pode resgatar)
CONTAS = [
    (1, 'marina.gomes', 'Marina Aguiar Gomes', 'Marina#Cred26', 500.0),
    (2, 'rodrigo.sena', 'Rodrigo Sena Vilela', 'Rodrigo#Cred26', 320.0),
    (3, 'helena.prado', 'Helena Prado Antunes', 'Helena#Cred26', 180.0),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT, saldo REAL
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), saldo) for i, login, nome, senha, saldo in CONTAS],
        )
