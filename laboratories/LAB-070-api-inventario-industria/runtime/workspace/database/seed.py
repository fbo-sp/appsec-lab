"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e faturas são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). Cada documento pertence a uma conta (``conta_id``).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'compras.metalfort', 'Metalfort Indústria de Peças Ltda.', 'Metalfort#Serra26', 'cliente'),
    (2, 'energia.valeverde', 'Têxtil Vale Verde S.A.', 'ValeVerde#Serra26', 'cliente'),
]

# (id, conta_id, título, data, detalhe)
DOCUMENTOS = [
    (101, 1, 'Fatura 10/2026 · unidade Contagem', '2026-11-02', 'Consumo 48.300 kWh · demanda 220 kW · R$ 41.870,15'),
    (102, 1, 'Fatura 09/2026 · unidade Contagem', '2026-10-02', 'Consumo 46.950 kWh · demanda 215 kW · R$ 40.112,80'),
    (201, 2, 'Fatura 10/2026 · fábrica Americana', '2026-11-02', 'Consumo 312.400 kWh · demanda 1.150 kW · R$ 268.905,40'),
    (202, 2, 'Fatura 09/2026 · fábrica Americana', '2026-10-02', 'Consumo 298.700 kWh · demanda 1.120 kW · R$ 257.340,10'),
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
            CREATE TABLE documentos (
                id INTEGER PRIMARY KEY, conta_id INTEGER REFERENCES contas(id), titulo TEXT, data TEXT, detalhe TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
        conexao.executemany("INSERT INTO documentos VALUES (?, ?, ?, ?, ?)", DOCUMENTOS)
