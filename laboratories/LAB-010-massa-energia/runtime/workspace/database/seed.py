"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, e-mail, telefone, perfil, categoria, senha)
USUARIOS = [
    (1, 'rafael.dutra', 'Rafael Dutra', 'comercial@dutraeletrica.example', '+55 51 99210-3030', 'fornecedor', 'padrao', 'Rafael@2026'),
    (2, 'vanessa.lobo', 'Vanessa Lobo', 'vendas@loboturbinas.example', '+55 41 98877-6655', 'fornecedor', 'estrategico', 'Vanessa@2026'),
    (3, 'marcos.compras', 'Marcos Teles Barros', 'marcos.barros@termoverde.example', '+55 51 3100-2290', 'comprador', 'estrategico', 'Compras#Termo26'),
]

# Parâmetros internos, visíveis só na Mesa de compras.
PARAMETROS = [("codigo_aprovacao_pedidos", "TMV-CMP-9054-RL")]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, email TEXT, telefone TEXT,
                perfil TEXT, categoria TEXT, senha_hash TEXT
            );
            CREATE TABLE parametros (nome TEXT PRIMARY KEY, valor TEXT);
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(*dados, generate_password_hash(senha)) for *dados, senha in USUARIOS],
        )
        conexao.executemany("INSERT INTO parametros VALUES (?, ?)", PARAMETROS)
