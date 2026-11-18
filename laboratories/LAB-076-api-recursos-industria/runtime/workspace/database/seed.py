"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e leituras são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). A conta de demonstração tem 3000 leituras, gerados a partir dos modelos abaixo.
"""

import os
import sqlite3
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'tiago.andrade', 'Tiago Andrade Moreira', 'Tiago#Ventura26', 'tecnico'),
]

TOTAL = 3000
PREFIXO = "LEI-"
# (descrição, valor) que se repetem ao longo do histórico
MODELOS = [
    ('AG-14 · vento 11,2 m/s · potência 2,9 MW', 2.9),
    ('AG-14 · vento 8,4 m/s · potência 1,7 MW', 1.7),
    ('AG-14 · vibração do mancal 3,1 mm/s', 3.1),
    ('AG-14 · temperatura do gerador 68 °C', 68.0),
    ('AG-14 · vento 14,9 m/s · potência 3,4 MW', 3.4),
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
