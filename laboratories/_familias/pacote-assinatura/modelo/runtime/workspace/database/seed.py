"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório (hash forte, werkzeug).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [[py:seed_contas]]

# (nome, descrição, valor em vigor, unidade)
PARAMETROS = [[py:seed_parametros]]

PACOTE_INICIAL = ("[[versao_inicial]]", "[[fornecedor]]")


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT, papel TEXT
            );
            CREATE TABLE parametros (nome TEXT PRIMARY KEY, descricao TEXT, valor TEXT, unidade TEXT);
            CREATE TABLE pacote_atual (versao TEXT, fornecedor TEXT);
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
        conexao.executemany("INSERT INTO parametros VALUES (?, ?, ?, ?)", PARAMETROS)
        conexao.execute("INSERT INTO pacote_atual VALUES (?, ?)", PACOTE_INICIAL)
