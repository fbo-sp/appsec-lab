"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório. Guardadas com hash forte
(werkzeug): o foco do laboratório não é o armazenamento da senha, e sim o limite de tentativas.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, saldo da conta)
CONTAS = [
    (1, 'marcos.tavares', 'Marcos Tavares Lima', 'Marcos#Lumen26', 0.0),
    (2, 'renata.borges', 'Renata Borges Pires', 'Renata#Lumen26', 0.0),
    (3, 'paulo.freitas', 'Paulo Freitas Nunes', 'Paulo#Lumen26', 0.0),
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
