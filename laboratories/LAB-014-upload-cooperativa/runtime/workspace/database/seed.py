"""Cria as tabelas, os dados FICTÍCIOS do banco e a pasta de anexos.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import shutil
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, perfil, senha)
USUARIOS = [
    (1, 'marcos.nunes', 'Marcos Nunes Valério', 'comum', 'Marcos#Cred26'),
    (2, 'regina.alves', 'Regina Alves Moura', 'equipe', 'Regina#Cred26'),
]

# (id do dono, descrição, nome do arquivo, enviado em). Os arquivos são cópias de amostras/documento.pdf.
ANEXOS = [
    (1, 'Holerite de março', 'comprovante-exemplo.pdf', '12/11/2026 09:20'),
]

AMOSTRA = os.path.join(os.path.dirname(__file__), "..", "amostras", "documento.pdf")


def criar_banco(caminho: str, pasta_anexos: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    shutil.rmtree(pasta_anexos, ignore_errors=True)
    os.makedirs(pasta_anexos)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, perfil TEXT, senha_hash TEXT
            );
            CREATE TABLE anexos (
                id INTEGER PRIMARY KEY AUTOINCREMENT, dono_id INTEGER, descricao TEXT, nome_arquivo TEXT,
                enviado_em TEXT DEFAULT (strftime('%d/%m/%Y %H:%M', 'now', '-3 hours'))
            );
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, perfil, generate_password_hash(senha)) for i, login, nome, perfil, senha in USUARIOS],
        )
        conexao.executemany(
            "INSERT INTO anexos (dono_id, descricao, nome_arquivo, enviado_em) VALUES (?, ?, ?, ?)", ANEXOS
        )
    for _, _, nome_arquivo, _ in ANEXOS:
        shutil.copyfile(AMOSTRA, os.path.join(pasta_anexos, nome_arquivo))
