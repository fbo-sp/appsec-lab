"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, celular do plantão, senha)
USUARIOS = [
    (1, 'leandro.vieira', 'Leandro Vieira Kunz', '+5551999991234', 'Leandro@2026'),
    (2, 'silvana.couto', 'Silvana Couto Ritter', '+5551977775555', 'Silvana@2026'),
]

# (id do usuário, quando, valor anterior, valor novo)
HISTORICO = [
    (1, '01/11/2026 07:00', '+5551988881111', '+5551999991234'),
    (2, '01/11/2026 19:00', '+5551966664444', '+5551977775555'),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, celular_plantao TEXT, senha_hash TEXT
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
