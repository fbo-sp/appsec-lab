"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e comprovantes são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). Cada documento pertence a uma conta (``conta_id``).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'larissa.prado', 'Larissa Prado Nunes', 'Larissa#Cobalto26', 'cliente'),
    (2, 'rogerio.tavares', 'Rogério Tavares Lima', 'Rogerio#Cobalto26', 'cliente'),
]

# (id, conta_id, título, data, detalhe)
DOCUMENTOS = [
    (101, 1, 'Pix enviado a Mercado Bom Preço', '2026-11-03', 'R$ 342,90 · chave CNPJ 12.345.678/0001-90 · Banco Cobalto'),
    (102, 1, 'Pix recebido de Ana Souza', '2026-11-09', 'R$ 1.200,00 · chave e-mail ana.souza@exemplo.com'),
    (201, 2, 'Pix enviado a Imobiliária Lar Certo', '2026-11-05', 'R$ 3.850,00 · aluguel · CPF ***.481.226-**'),
    (202, 2, 'Pix recebido de Construtora Alicerce', '2026-11-10', 'R$ 12.400,00 · salário'),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, senha_hash TEXT, papel TEXT
            );
            CREATE TABLE documentos (
                id INTEGER PRIMARY KEY, conta_id INTEGER REFERENCES contas(id), titulo TEXT, data TEXT, detalhe TEXT
            );
            """
        )
        conexao.executemany(
            "INSERT INTO contas VALUES (?, ?, ?, ?, ?)",
            [(i, login, nome, generate_password_hash(senha), papel) for i, login, nome, senha, papel in CONTAS],
        )
        conexao.executemany("INSERT INTO documentos VALUES (?, ?, ?, ?, ?)", DOCUMENTOS)
