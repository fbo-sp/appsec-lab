"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, [[campo_label_minusculo]], senha)
USUARIOS = [[py:seed_usuarios]]

# (id do usuário, quando, valor anterior, valor novo)
HISTORICO = [[py:seed_historico]]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, [[campo]] TEXT, senha_hash TEXT
            );
            CREATE TABLE historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, quando TEXT,
                valor_anterior TEXT, valor_novo TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?)",
            [(*dados, generate_password_hash(senha)) for *dados, senha in USUARIOS],
        )
        conexao.executemany(
            "INSERT INTO historico (usuario_id, quando, valor_anterior, valor_novo) VALUES (?, ?, ?, ?)",
            HISTORICO,
        )
