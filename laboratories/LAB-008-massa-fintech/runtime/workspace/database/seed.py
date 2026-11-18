"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, e-mail, telefone, perfil, pacote, senha)
USUARIOS = [
    (1, 'bruno.sales', 'Bruno Sales Teixeira', 'bruno.sales@email.example', '+55 11 98888-1020', 'cliente', 'essencial', 'Bruno@2026'),
    (2, 'lia.moura', 'Lia Moura Campos', 'lia.moura@email.example', '+55 21 97777-3344', 'cliente', 'private', 'Lia@2026'),
    (3, 'otavio.analista', 'Otávio Reis Nogueira', 'otavio.reis@trilhapay.example', '+55 11 3000-4410', 'analista', 'private', 'Analista#Trilha26'),
]

# Parâmetros internos, visíveis só na Backoffice de crédito.
PARAMETROS = [("codigo_aprovacao_turno", "TRP-LIM-6630-PZ")]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, email TEXT, telefone TEXT,
                perfil TEXT, pacote TEXT, senha_hash TEXT
            );
            CREATE TABLE parametros (nome TEXT PRIMARY KEY, valor TEXT);
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(*dados, generate_password_hash(senha)) for *dados, senha in USUARIOS],
        )
        conexao.executemany("INSERT INTO parametros VALUES (?, ?)", PARAMETROS)
