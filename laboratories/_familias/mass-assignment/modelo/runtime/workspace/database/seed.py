"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, e-mail, telefone, perfil, [[campo]], senha)
USUARIOS = [[py:seed_usuarios]]

# Parâmetros internos, visíveis só na [[area_priv_titulo]].
PARAMETROS = [("[[chave_priv_nome]]", "[[chave_priv]]")]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, email TEXT, telefone TEXT,
                perfil TEXT, [[campo]] TEXT, senha_hash TEXT
            );
            CREATE TABLE parametros (nome TEXT PRIMARY KEY, valor TEXT);
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(*dados, generate_password_hash(senha)) for *dados, senha in USUARIOS],
        )
        conexao.executemany("INSERT INTO parametros VALUES (?, ?)", PARAMETROS)
