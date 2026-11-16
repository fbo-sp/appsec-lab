"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, e-mail para envio de laudos, senha)
USUARIOS = [
    (1, 'beatriz.lima', 'Beatriz Lima Duarte', 'beatriz.lima@email.example', 'Beatriz@2026'),
    (2, 'joao.pedro', 'João Pedro Antunes', 'joao.antunes@email.example', 'JoaoP@2026'),
]

# (id do usuário, quando, valor anterior, valor novo)
HISTORICO = [
    (1, '28/10/2026 18:02', 'beatriz.duarte@email.example', 'beatriz.lima@email.example'),
    (2, '25/10/2026 08:15', 'jp.antunes@email.example', 'joao.antunes@email.example'),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, email_laudos TEXT, senha_hash TEXT
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
