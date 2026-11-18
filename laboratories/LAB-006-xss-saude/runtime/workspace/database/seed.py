"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, perfil, senha, segredo do cookie da sessão no navegador)
USUARIOS = [
    (1, 'julia.andrade', 'Júlia Andrade Lima', 'comum', 'Julia@2026', 'LUM-APP-5D2R-8814'),
    (2, 'paulo.mendes', 'Paulo Mendes Rocha', 'comum', 'Paulo@2026', 'LUM-APP-9H3T-1127'),
    (3, 'carla.atendente', 'Carla Menezes Farias', 'equipe', 'Atende#Lumina26', 'LUM-ATD-2290-QZ'),
]

# (id do dono, Exame, Unidade, Observação para a coleta)
EXAMES = [
    (1, 'Hemograma completo', 'Unidade Centro', 'Em jejum desde as 22h'),
    (1, 'Vitamina D (25-OH)', 'Unidade Centro', 'Uso suplemento'),
    (1, 'Glicemia de jejum', 'Unidade Jardins', 'Prefiro coleta cedo'),
    (1, 'TSH e T4 livre', 'Unidade Jardins', ''),
    (2, 'Ressonância magnética de joelho', 'Unidade Paulista', 'Tenho claustrofobia leve'),
    (2, 'Hemograma completo', 'Unidade Paulista', ''),
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
            CREATE TABLE exames (
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
            "INSERT INTO exames (dono_id, nome, detalhe, nota) VALUES (?, ?, ?, ?)", EXAMES
        )
