"""Cria as tabelas e os dados FICTÍCIOS da clínica.

Atenção: os CPFs abaixo têm dígitos verificadores inválidos de propósito e os e-mails usam o domínio
reservado ``.example``. Nenhum dado pertence a uma pessoa real.
"""

import sqlite3

MEDICOS = [
    ("Ana Beatriz Souza", "Cardiologia", "CRM-SP 104233"),
    ("Carlos Menezes", "Ortopedia", "CRM-SP 087541"),
    ("Joana D'Ávila", "Pediatria", "CRM-SP 123456"),
    ("Marcos Tanaka", "Dermatologia", "CRM-SP 156780"),
    ("Patrícia Lima", "Clínica geral", "CRM-SP 099812"),
    ("Rafael Oliveira", "Neurologia", "CRM-SP 141907"),
]

PACIENTES = [
    ("Helena Martins", "helena.martins@pacientes.vidaplena.example", "123.456.789-00", "Hipertensão"),
    ("Bruno Carvalho", "bruno.carvalho@pacientes.vidaplena.example", "987.654.321-99", "Asma"),
    ("Lúcia Fernandes", "lucia.fernandes@pacientes.vidaplena.example", "111.222.333-44", "Diabetes tipo 2"),
    ("Diego Ramos", "diego.ramos@pacientes.vidaplena.example", "555.666.777-11", "Enxaqueca"),
]

CONFIGURACOES = [
    ("versao_portal", "2.4.1"),
    ("token_integracao_laboratorio", "VP-INT-7Q2K-93XD"),
]


def criar_banco(caminho: str) -> None:
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            DROP TABLE IF EXISTS medicos;
            DROP TABLE IF EXISTS pacientes;
            DROP TABLE IF EXISTS configuracoes;
            CREATE TABLE medicos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                especialidade TEXT NOT NULL,
                crm TEXT NOT NULL
            );
            CREATE TABLE pacientes (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                cpf TEXT NOT NULL,
                condicao TEXT NOT NULL
            );
            CREATE TABLE configuracoes (chave TEXT PRIMARY KEY, valor TEXT NOT NULL);
            """
        )
        conexao.executemany("INSERT INTO medicos (nome, especialidade, crm) VALUES (?, ?, ?)", MEDICOS)
        conexao.executemany(
            "INSERT INTO pacientes (nome, email, cpf, condicao) VALUES (?, ?, ?, ?)", PACIENTES
        )
        conexao.executemany("INSERT INTO configuracoes (chave, valor) VALUES (?, ?)", CONFIGURACOES)
