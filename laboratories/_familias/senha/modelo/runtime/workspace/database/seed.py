"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.

As contas foram "importadas" do sistema legado "[[sistema_legado]]": a senha de cada uma é guardada
exatamente como aquele sistema guardava, pelo mesmo resumo (a falha que você vai corrigir).
"""

import hashlib
import os
import sqlite3

# (id, login, nome, senha fictícia como estava no sistema legado)
USUARIOS = [[py:seed_usuarios]]


def _resumo_legado(senha: str) -> str:
    """O mesmo resumo que o sistema legado usava para guardar a senha."""
    return hashlib.md5(senha.encode()).hexdigest()


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?)",
            [(i, login, nome, _resumo_legado(senha)) for i, login, nome, senha in USUARIOS],
        )
