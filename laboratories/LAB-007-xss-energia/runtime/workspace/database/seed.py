"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, perfil, senha, segredo do cookie da sessão no navegador)
USUARIOS = [
    (1, 'tiago.nunes', 'Tiago Nunes Batista', 'comum', 'Campo@2026', 'VOL-TAB-4C7N-6602'),
    (2, 'bruna.teixeira', 'Bruna Teixeira Lopes', 'comum', 'Bruna@2026', 'VOL-TAB-8M1K-3390'),
    (3, 'helena.cod', 'Helena Duarte Vaz', 'equipe', 'Operador#Volt26', 'VOL-MNB-7718-TW'),
]

# (id do dono, Equipamento, Subestação, Relato do técnico)
ORDENS = [
    (1, 'Religador R-12 (Alim. 04)', 'SE Vale Verde', 'Disparo intermitente após chuva'),
    (1, 'Transformador TR-2 13,8 kV', 'SE Centro', 'Ruído acima do normal'),
    (1, 'Chave seccionadora CS-31', 'SE Vale Verde', 'Inspeção termográfica'),
    (2, 'Banco de capacitores BC-7', 'SE Porto Novo', 'Fusível queimado'),
    (2, 'Religador R-03 (Alim. 11)', 'SE Porto Novo', ''),
]


def criar_banco(caminho: str) -> None:
    if os.path.exists(caminho):
        os.remove(caminho)
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, login TEXT UNIQUE, nome TEXT, perfil TEXT,
                senha_hash TEXT, segredo TEXT
            );
            CREATE TABLE ordens (
                id INTEGER PRIMARY KEY AUTOINCREMENT, dono_id INTEGER, nome TEXT, detalhe TEXT, nota TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conexao.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?)",
            [(i, login, nome, perfil, generate_password_hash(senha), segredo)
             for i, login, nome, perfil, senha, segredo in USUARIOS],
        )
        conexao.executemany(
            "INSERT INTO ordens (dono_id, nome, detalhe, nota) VALUES (?, ?, ?, ?)", ORDENS
        )
