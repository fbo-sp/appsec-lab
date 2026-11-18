"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e requisições são inventados e as senhas existem só neste laboratório (hash
forte, werkzeug). A tabela ``consultas`` guarda o que o Rolamax respondeu.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'marcos.teixeira', 'Marcos Teixeira Bastos', 'Marcos#Alvorada26', 'comprador'),
]

# (referência, conta_id, descrição)
PENDENCIAS = [
    ('COT-7781', 1, 'Rolamento autocompensador 22230 · laminador de tiras · 4 unidades'),
    ('COT-7782', 1, 'Rolamento de rolos cônicos 32222 · ponte rolante · 2 unidades'),
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
            CREATE TABLE pendencias (referencia TEXT PRIMARY KEY, conta_id INTEGER, descricao TEXT);
            CREATE TABLE consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT, conta_id INTEGER, referencia TEXT, valor REAL, status TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
        conexao.executemany("INSERT INTO pendencias VALUES (?, ?, ?)", PENDENCIAS)
