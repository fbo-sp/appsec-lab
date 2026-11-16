"""Cria as tabelas e os dados FICTÍCIOS do banco.

Nomes, documentos e e-mails são inventados (domínio reservado ``.example``) e as senhas existem só neste
laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# (id, login, nome, perfil, senha, segredo do cookie da sessão no navegador)
USUARIOS = [
    (1, 'marina.costa', 'Marina Costa Ribeiro', 'comum', 'Marina@2026', 'AUR-DSP-7Q4M-2210'),
    (2, 'rodrigo.lima', 'Rodrigo Tavares Lima', 'comum', 'Rodrigo@2026', 'AUR-DSP-3K8P-4471'),
    (3, 'renata.gerente', 'Renata Alves Pacheco', 'equipe', 'Gerente#Aurora26', 'AUR-APR-5531-KX'),
]

# (id do dono, Nome do favorecido, Chave PIX, Apelido)
FAVORECIDOS = [
    (1, 'Ana Paula Souza', 'ana.souza@email.example', 'Faxina quinzenal'),
    (1, "Padaria D'Ávila Ltda", '12.345.678/0001-**', 'Pão de sexta'),
    (1, 'Condomínio Jardim das Flores', 'condominio@jardimflores.example', 'Condomínio'),
    (1, 'Luciana Prado', '+55 11 9****-3321', 'Aluguel'),
    (2, 'Mariana Lopes', 'mariana.lopes@email.example', 'Irmã'),
    (2, 'Escola Pequeno Saber Ltda', 'financeiro@pequenosaber.example', 'Mensalidade'),
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
            CREATE TABLE favorecidos (
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
            "INSERT INTO favorecidos (dono_id, nome, detalhe, nota) VALUES (?, ?, ?, ?)", FAVORECIDOS
        )
