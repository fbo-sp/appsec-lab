"""Cria a tabela e os dados FICTÍCIOS de contas (os funcionários que fazem login).

Nomes, logins e senhas são inventados e só existem neste laboratório. As senhas são guardadas com
hash forte (werkzeug): o login não é o foco do laboratório. O foco é a BUSCA no diretório (veja
services/busca_service.py e diretorio.py).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia) — funcionários que entram no painel.
CONTAS = [
    (1, 'ti.suporte', 'Equipe de TI', 'TI#Aurora26'),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha)) for i, login, nome, senha in CONTAS],
        )
