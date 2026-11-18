"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e lançamentos são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). A conta de demonstração tem 3000 lançamentos, gerados a partir dos modelos abaixo.
"""

import os
import sqlite3
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'eduardo.saraiva', 'Eduardo Saraiva Monteiro', 'Eduardo#Pinaculo26', 'cliente'),
]

TOTAL = 3000
PREFIXO = "LCT-"
# (descrição, valor) que se repetem ao longo do histórico
MODELOS = [
    ('Compra de ações PNXA4', -1520.4),
    ('Dividendos PNXA4', 86.75),
    ('Aplicação CDB Pináculo 110% CDI', -5000.0),
    ('Resgate Tesouro Selic', 2310.18),
    ('Taxa de custódia', -12.9),
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
