"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e senhas são inventados e só existem neste laboratório (hash forte, werkzeug). Cada
pedido pertence a UM usuário (``dono_id``). O foco do laboratório é a resolução do pedido na API
GraphQL (services/pedido_service.py), que deve devolver só os pedidos do dono logado.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia) — usuários que fazem login.
CONTAS = [
    (1, 'ana.ribeiro', 'Ana Ribeiro Teixeira', 'Ana#Pagomais26'),
    (2, 'carlos.moura', 'Carlos Moura Pinto', 'Carlos#Pagomais26'),
]
# (id, dono_id, descrição, valor) — cada pedido pertence ao usuário dono_id.
PEDIDOS = [
    (1, 1, 'Pagamento ao fornecedor Vale Insumos', 1250.0),
    (2, 2, 'Pagamento ao fornecedor Norte Logistica', 2300.0),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT
            );
            CREATE TABLE pedidos (
                id INTEGER PRIMARY KEY, dono_id INTEGER, descricao TEXT, valor REAL
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha)) for i, login, nome, senha in CONTAS],
        )
        conexao.executemany("INSERT INTO pedidos VALUES (?, ?, ?, ?)", [tuple(p) for p in PEDIDOS])
