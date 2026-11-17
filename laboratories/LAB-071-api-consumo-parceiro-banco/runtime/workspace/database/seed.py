"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e propostas são inventados e as senhas existem só neste laboratório (hash
forte, werkzeug). A tabela ``consultas`` guarda o que o Bureau Sigma respondeu.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'renata.quintela', 'Renata Quintela Dias', 'Renata#Vertix26', 'analista'),
]

# (referência, conta_id, descrição)
PENDENCIAS = [
    ('PROP-4471', 1, 'Cartão Vértix Gold · cliente Júlio César Prado · renda declarada R$ 7.800'),
    ('PROP-4472', 1, 'Cartão Vértix Básico · cliente Sônia Abreu Lima · renda declarada R$ 3.100'),
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
