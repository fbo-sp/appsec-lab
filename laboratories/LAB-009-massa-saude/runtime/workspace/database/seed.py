"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, e-mail, telefone, perfil, plano, senha)
USUARIOS = [
    (1, 'paula.mendes', 'Paula Mendes Rocha', 'paula.mendes@email.example', '+55 31 98123-4455', 'beneficiario', 'regional', 'Paula@2026'),
    (2, 'jorge.batista', 'Jorge Batista Lins', 'jorge.batista@email.example', '+55 31 99654-7788', 'beneficiario', 'nacional-premium', 'Jorge@2026'),
    (3, 'silvia.auditora', 'Sílvia Andrade Prado', 'silvia.prado@serenosaude.example', '+55 31 3200-1180', 'auditor', 'nacional-premium', 'Auditoria#Sereno26'),
]

# Parâmetros internos, visíveis só na Auditoria médica.
PARAMETROS = [("senha_liberacao_dia", "SER-AUD-3381-MV")]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, email TEXT, telefone TEXT,
                perfil TEXT, plano TEXT, senha_hash TEXT
            );
            CREATE TABLE parametros (nome TEXT PRIMARY KEY, valor TEXT);
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(*dados, generate_password_hash(senha)) for *dados, senha in USUARIOS],
        )
        conexao.executemany("INSERT INTO parametros VALUES (?, ?)", PARAMETROS)
