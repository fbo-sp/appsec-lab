"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes e logins são inventados e as senhas existem só neste laboratório (hash forte, werkzeug).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'beatriz.nogueira', 'Beatriz Nogueira Sales', 'Beatriz#Solaris26', 'analista'),
]

# (nome, descrição, valor em vigor, unidade)
PARAMETROS = [
    ('limite_pix_noturno', 'Valor máximo de Pix entre 20h e 6h sem análise', 1000, 'R$'),
    ('score_minimo_aprovacao', 'Score mínimo para aprovar sem análise', 700, 'pontos'),
    ('dias_dispositivo_novo', 'Dias de quarentena de um dispositivo novo', 3, 'dias'),
]

PACOTE_INICIAL = ("2026.10.3", "Bureau Atento Antifraude")


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
