"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório (hash forte, werkzeug). Cada
conta tem um papel: ``comum`` ou ``admin``. O papel decide quem pode usar as funções administrativas.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'sandra.rocha', 'Sandra Rocha Peixoto', 'Sandra#SantaClara26', 'admin'),
    (2, 'pedro.alves', 'Pedro Alves Macedo', 'Pedro#SantaClara26', 'comum'),
    (3, 'marta.lopes', 'Marta Lopes Brandão', 'Marta#SantaClara26', 'comum'),
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
