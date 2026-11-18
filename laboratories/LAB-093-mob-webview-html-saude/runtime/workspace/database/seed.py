"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins, documentos e senhas são inventados e só existem neste laboratório (senhas com hash
forte, werkzeug). Cada item da lista pertence a UM usuário (``dono_id``).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, resumo da tela inicial, documento, dado pessoal)
CONTAS = [
    (1, 'marcos.tavares', 'Marcos Tavares Lima', 'Marcos#Lumen26', 'Próxima consulta 20/11 às 14h30', '333.666.999-57', 'CID J45 asma'),
    (2, 'renata.borges', 'Renata Borges Nunes', 'Renata#Lumen26', 'Próxima consulta 02/12 às 9h', '444.777.000-68', 'CID E11 diabetes'),
]
# (id, dono_id, título, detalhe, valor) — cada item pertence ao usuário dono_id.
ITENS = [
    (1, 1, 'Hemograma completo', 'Resultado disponível', '12/11'),
    (2, 1, 'Consulta cardiologia', 'Agendada', '20/11'),
    (3, 2, 'Ressonância de joelho', 'Laudo em análise', '08/11'),
]
# (destinatario_id, autor, texto, enviada em) — mensagens que já estão na central.
MENSAGENS = [
    (1, 'Clínica Lumen', 'Seu exame Hemograma completo já está disponível.', '15/11 08:10'),
    (1, 'Renata Borges Nunes', 'Convite: indiquei você para o programa Lumen Bem-Estar.', '16/11 19:22'),
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
            CREATE TABLE mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT, destinatario_id INTEGER, autor TEXT, texto TEXT, enviada_em TEXT
            );
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
        conexao.executemany(
            "INSERT INTO mensagens (destinatario_id, autor, texto, enviada_em) VALUES (?, ?, ?, ?)", MENSAGENS
        )
