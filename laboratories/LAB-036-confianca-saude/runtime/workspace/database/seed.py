"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório (hash forte, werkzeug). O
saldo de cada conta é em pontos; os produtos têm um custo em pontos definido pela loja (no servidor).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, saldo em pontos)
CONTAS = [
    (1, 'rafael.antunes', 'Rafael Antunes Barreto', 'Rafael#Sereno26', 500.0),
    (2, 'carla.menezes', 'Carla Menezes Pires', 'Carla#Sereno26', 500.0),
    (3, 'bruno.dias', 'Bruno Dias Correia', 'Bruno#Sereno26', 500.0),
]

# (id, nome do produto, custo em pontos) — o custo é definido pela loja, no servidor.
PRODUTOS = [
    (1, 'Smartband de atividades', 300),
    (2, 'Kit de faixas de exercício', 150),
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
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY, nome TEXT, custo INTEGER
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), saldo) for i, login, nome, senha, saldo in CONTAS],
        )
        conexao.executemany("INSERT INTO produtos VALUES (?, ?, ?)", PRODUTOS)
