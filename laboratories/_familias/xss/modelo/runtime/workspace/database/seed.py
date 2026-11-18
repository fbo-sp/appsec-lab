"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, perfil, senha, segredo do cookie da sessão no navegador)
USUARIOS = [[py:seed_usuarios]]

# (id do dono, [[label_nome]], [[label_detalhe]], [[label_nota]])
[[ENTIDADES]] = [[py:seed_itens]]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, perfil TEXT,
                senha_hash TEXT, segredo TEXT
            );
            CREATE TABLE [[tabela]] (
                id INTEGER PRIMARY KEY AUTOINCREMENT, dono_id INTEGER, nome TEXT, detalhe TEXT, nota TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?)",
            [(i, login, nome, perfil, generate_password_hash(senha), segredo)
             for i, login, nome, perfil, senha, segredo in USUARIOS],
        )
        conexao.executemany(
            "INSERT INTO [[tabela]] (dono_id, nome, detalhe, nota) VALUES (?, ?, ?, ?)", [[ENTIDADES]]
        )
