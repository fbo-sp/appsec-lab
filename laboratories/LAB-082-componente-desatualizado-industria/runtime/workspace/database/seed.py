"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório (hash forte, werkzeug).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'diego.carvalho', 'Diego Carvalho Neves', 'Diego#FerroNorte26', 'tecnico'),
]

# (conta_id, data, descrição, valor)
ITENS = [
    (1, '2026-11-05', 'OS-31877 · Troca de rolamento da ponte rolante 3', 'Programada'),
    (1, '2026-11-08', 'OS-31902 · Inspeção do redutor do laminador', 'Em execução'),
    (1, '2026-11-13', 'OS-31940 · Lubrificação da correia transportadora C-12', 'Aberta'),
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
            CREATE TABLE itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT, conta_id INTEGER, data TEXT, descricao TEXT, valor TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
        conexao.executemany("INSERT INTO itens (conta_id, data, descricao, valor) VALUES (?, ?, ?, ?)", ITENS)
