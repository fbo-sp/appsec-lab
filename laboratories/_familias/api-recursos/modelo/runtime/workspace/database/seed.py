"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e [[recurso_plural]] são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). A conta de demonstração tem [[total]] [[recurso_plural]], gerados a partir dos modelos abaixo.
"""

import os
import sqlite3
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [[py:seed_contas]]

TOTAL = [[total]]
PREFIXO = "[[prefixo]]"
# (descrição, valor) que se repetem ao longo do histórico
MODELOS = [[py:modelos]]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT, papel TEXT
            );
            CREATE TABLE registros (
                id INTEGER PRIMARY KEY, conta_id INTEGER, data TEXT, descricao TEXT, valor REAL
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
        hoje = date(2026, 11, 17)
        registros = []
        for n in range(1, TOTAL + 1):
            descricao, valor = MODELOS[n % len(MODELOS)]
            dia = (hoje - timedelta(hours=n * 3)).isoformat()
            registros.append((n, 1, dia, f"{PREFIXO}{n:05d} · {descricao}", valor))
        conexao.executemany("INSERT INTO registros VALUES (?, ?, ?, ?, ?)", registros)
