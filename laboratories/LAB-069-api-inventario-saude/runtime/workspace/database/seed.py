"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, logins e exames são inventados e as senhas existem só neste laboratório (hash forte,
werkzeug). Cada documento pertence a uma conta (``conta_id``).
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, senha fictícia, papel)
CONTAS = [
    (1, 'beatriz.moura', 'Beatriz Moura Campos', 'Beatriz#Iris26', 'paciente'),
    (2, 'otavio.ramos', 'Otávio Ramos Bezerra', 'Otavio#Iris26', 'paciente'),
]

# (id, conta_id, título, data, detalhe)
DOCUMENTOS = [
    (101, 1, 'Hemograma completo', '2026-11-04', 'Hemoglobina 13,8 g/dL · leucócitos 6.200/mm³ · dentro da referência'),
    (102, 1, 'Glicemia de jejum', '2026-11-04', '92 mg/dL · referência 70 a 99 mg/dL'),
    (201, 2, 'Sorologia para hepatite C', '2026-11-06', 'Anti-HCV reagente · repetir com PCR · médico solicitante CRM-SP 123456'),
    (202, 2, 'Perfil lipídico', '2026-11-06', 'LDL 168 mg/dL · acima do recomendado'),
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
