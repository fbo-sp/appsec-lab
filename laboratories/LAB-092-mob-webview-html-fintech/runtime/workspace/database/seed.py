"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins, documentos e senhas são inventados e só existem neste laboratório (senhas com hash
forte, werkzeug). Cada item da lista pertence a UM usuário (``dono_id``).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, resumo da tela inicial, documento, dado pessoal)
CONTAS = [
    (1, 'ana.ribeiro', 'Ana Ribeiro Teixeira', 'Ana#Pagomais26', 'Saldo R$ 4.820,15', '111.444.777-35', 'Renda mensal R$ 9.800'),
    (2, 'carlos.moura', 'Carlos Moura Pinto', 'Carlos#Pagomais26', 'Saldo R$ 12.310,00', '222.555.888-46', 'Renda mensal R$ 15.200'),
]
# (id, dono_id, título, detalhe, valor) — cada item pertence ao usuário dono_id.
ITENS = [
    (1, 1, 'PIX recebido', 'Vale Insumos', '+ R$ 1.250,00'),
    (2, 1, 'Cartão final 4410', 'Mercado Norte', '- R$ 212,90'),
    (3, 2, 'PIX enviado', 'Norte Transportes', '- R$ 2.300,00'),
]
# (destinatario_id, autor, texto, enviada em) — mensagens que já estão na central.
MENSAGENS = [
    (1, 'Pagomais Atendimento', 'Seu cartão final 4410 foi enviado. Acompanhe a entrega pelo app.', '15/11 10:02'),
    (1, 'Carlos Moura Pinto', 'Pix de R$ 35,00: valeu pelo almoço!', '16/11 13:40'),
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
