"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins, documentos e senhas são inventados e só existem neste laboratório (senhas com hash
forte, werkzeug). Cada item da lista pertence a UM usuário (``dono_id``).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, resumo da tela inicial, documento, dado pessoal)
CONTAS = [
    (1, 'diego.campos', 'Diego Campos Ferraz', 'Diego#Aurora26', '3 ordens em aberto hoje', 'MAT-40213', 'Rua das Turbinas 120'),
    (2, 'sonia.barros', 'Sonia Barros Teles', 'Sonia#Aurora26', '1 ordem em aberto hoje', 'MAT-40877', 'Avenida da Usina 45'),
]
# (id, dono_id, título, detalhe, valor) — cada item pertence ao usuário dono_id.
ITENS = [
    (1, 1, 'OS 4821', 'Manutenção da bomba 4', 'Hoje'),
    (2, 1, 'OS 4822', 'Inspeção da subestação 2', 'Amanhã'),
    (3, 2, 'OS 4825', 'Parada da turbina 2', '19/11'),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT,
                resumo TEXT, documento TEXT, dado_pessoal TEXT
            );
            CREATE TABLE itens (
                id INTEGER PRIMARY KEY, dono_id INTEGER, titulo TEXT, detalhe TEXT, valor TEXT
            );
            CREATE TABLE tokens (token TEXT PRIMARY KEY, conta_id INTEGER, ativo INTEGER);
            CREATE TABLE provas (prova TEXT PRIMARY KEY, conta_id INTEGER, criada_em REAL);
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (i, login, nome, generate_password_hash(senha), resumo, doc, pessoal)
                for i, login, nome, senha, resumo, doc, pessoal in CONTAS
            ],
        )
        conexao.executemany("INSERT INTO itens VALUES (?, ?, ?, ?, ?)", [tuple(i) for i in ITENS])

