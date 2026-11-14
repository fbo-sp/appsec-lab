"""Cria as tabelas e os dados FICTÍCIOS do banco.

Atenção: documentos aparecem mascarados, e-mails e chaves PIX usam o domínio reservado ``.example`` e
as senhas existem só neste laboratório. Nenhum dado pertence a uma pessoa ou empresa real.
"""

import sqlite3

from werkzeug.security import generate_password_hash

# (id, nome, documento, agência, conta, e-mail, senha)
CLIENTES = [
    (1, "Marina Costa Ribeiro", "***.482.917-**", "0001", "48213-7",
     "marina.ribeiro@clientes.vertice.example", "Marina@2026"),
    (2, "Rodrigo Tavares Lima", "***.736.205-**", "0001", "51907-2",
     "rodrigo.lima@clientes.vertice.example", "Rodrigo@2026"),
    (3, "Indústria Têxtil Serra Azul S.A.", "78.123.456/0001-**", "0001", "10022-5",
     "tesouraria@serraazul.example", "SerraAzul#Tesouraria9"),
    (4, "Juliana Prado Mendes", "***.219.664-**", "0001", "63318-0",
     "juliana.mendes@clientes.vertice.example", "Juliana@2026"),
    (5, "Felipe Andrade Nogueira", "***.903.551-**", "0001", "70245-9",
     "felipe.nogueira@clientes.vertice.example", "Felipe@2026"),
    (6, "Comercial Ribeirão Alimentos Ltda", "81.654.321/0001-**", "0001", "22870-4",
     "financeiro@ribeiraoalimentos.example", "Ribeirao#Fin2026"),
]

# (número, id do cliente pagador, data e hora, valor em centavos, recebedor, documento do recebedor,
#  chave PIX, identificador da transação)
PIX_ENVIADOS = [
    (10421, 3, '2026-11-03 10:06', 720150, 'Supermercado Bom Preço Ltda', '12.345.678/0001-**', 'pagamentos@bompreco.example', 'E90817264202611031006A0000010421'),
    (10422, 3, '2026-11-03 12:37', 489000, 'Imobiliária Nova Casa Ltda', '45.678.901/0001-**', 'aluguel@novacasa.example', 'E90817264202611031237A0000010422'),
    (10423, 3, '2026-11-03 15:45', 720150, 'Supermercado Bom Preço Ltda', '12.345.678/0001-**', 'pagamentos@bompreco.example', 'E90817264202611031545A0000010423'),
    (10424, 1, '2026-11-03 19:30', 315050, 'Thiago Moreira Lopes', '***.045.996-**', 'thiago.lopes@email.example', 'E90817264202611031930A0000010424'),
    (10425, 5, '2026-11-04 08:15', 99900, 'Supermercado Bom Preço Ltda', '12.345.678/0001-**', 'pagamentos@bompreco.example', 'E90817264202611040815A0000010425'),
    (10426, 2, '2026-11-04 10:14', 72015, 'Escola Pequeno Saber Ltda', '23.456.789/0001-**', 'financeiro@pequenosaber.example', 'E90817264202611041014A0000010426'),
    (10427, 6, '2026-11-04 12:50', 240000, 'Clínica Sorriso Odontologia', '34.567.890/0001-**', '+55 11 3****-2200', 'E90817264202611041250A0000010427'),
    (10428, 5, '2026-11-04 16:03', 99900, 'Lucas Ferreira Alves', '***.318.447-**', 'lucas.alves@email.example', 'E90817264202611041603A0000010428'),
    (10429, 2, '2026-11-04 19:53', 240000, 'Aline Souza Barros', '***.561.882-**', '+55 21 9****-7731', 'E90817264202611041953A0000010429'),
    (10430, 3, '2026-11-05 00:20', 3150500, 'Pedro Henrique Matos', '***.774.230-**', 'pedro.matos@email.example', 'E90817264202611050020A0000010430'),
    (10431, 1, '2026-11-05 02:24', 189990, 'Lucas Ferreira Alves', '***.318.447-**', 'lucas.alves@email.example', 'E90817264202611050224A0000010431'),
    (10432, 6, '2026-11-05 05:05', 135000, 'Clínica Sorriso Odontologia', '34.567.890/0001-**', '+55 11 3****-2200', 'E90817264202611050505A0000010432'),
    (10433, 3, '2026-11-05 08:23', 48790000, 'Construtora Pedra Alta Ltda', '67.890.123/0001-**', 'obras@pedraalta.example', 'E90817264202611050823A0000010433'),
    (10434, 6, '2026-11-05 12:18', 189990, 'Camila Rocha Duarte', '***.902.115-**', '+55 11 9****-4410', 'E90817264202611051218A0000010434'),
    (10435, 2, '2026-11-05 16:50', 35000, 'Imobiliária Nova Casa Ltda', '45.678.901/0001-**', 'aluguel@novacasa.example', 'E90817264202611051650A0000010435'),
    (10436, 6, '2026-11-05 18:59', 8990, 'Escola Pequeno Saber Ltda', '23.456.789/0001-**', 'financeiro@pequenosaber.example', 'E90817264202611051859A0000010436'),
    (10437, 4, '2026-11-06 08:27', 12000, 'Escola Pequeno Saber Ltda', '23.456.789/0001-**', 'financeiro@pequenosaber.example', 'E90817264202611060827A0000010437'),
    (10438, 5, '2026-11-06 11:50', 135000, 'Camila Rocha Duarte', '***.902.115-**', '+55 11 9****-4410', 'E90817264202611061150A0000010438'),
    (10439, 1, '2026-11-06 15:50', 135000, 'Escola Pequeno Saber Ltda', '23.456.789/0001-**', 'financeiro@pequenosaber.example', 'E90817264202611061550A0000010439'),
    (10440, 6, '2026-11-06 17:27', 189990, 'Escola Pequeno Saber Ltda', '23.456.789/0001-**', 'financeiro@pequenosaber.example', 'E90817264202611061727A0000010440'),
    (10441, 2, '2026-11-06 19:41', 15075, 'Clínica Sorriso Odontologia', '34.567.890/0001-**', '+55 11 3****-2200', 'E90817264202611061941A0000010441'),
    (10442, 4, '2026-11-07 08:22', 35000, 'Clínica Sorriso Odontologia', '34.567.890/0001-**', '+55 11 3****-2200', 'E90817264202611070822A0000010442'),
    (10443, 5, '2026-11-07 11:50', 15075, 'Auto Peças Rota 66 Ltda', '56.789.012/0001-**', 'vendas@rota66.example', 'E90817264202611071150A0000010443'),
    (10444, 3, '2026-11-07 15:55', 2400000, 'Clínica Sorriso Odontologia', '34.567.890/0001-**', '+55 11 3****-2200', 'E90817264202611071555A0000010444'),
    (10445, 4, '2026-11-07 17:37', 72015, 'Auto Peças Rota 66 Ltda', '56.789.012/0001-**', 'vendas@rota66.example', 'E90817264202611071737A0000010445'),
    (10446, 1, '2026-11-07 19:56', 48900, 'Supermercado Bom Preço Ltda', '12.345.678/0001-**', 'pagamentos@bompreco.example', 'E90817264202611071956A0000010446'),
    (10447, 6, '2026-11-08 08:17', 35000, 'Supermercado Bom Preço Ltda', '12.345.678/0001-**', 'pagamentos@bompreco.example', 'E90817264202611080817A0000010447'),
    (10448, 3, '2026-11-08 11:50', 150750, 'Aline Souza Barros', '***.561.882-**', '+55 21 9****-7731', 'E90817264202611081150A0000010448'),
    (10449, 6, '2026-11-08 16:00', 2590, 'Thiago Moreira Lopes', '***.045.996-**', 'thiago.lopes@email.example', 'E90817264202611081600A0000010449'),
    (10450, 4, '2026-11-08 17:47', 8990, 'Lucas Ferreira Alves', '***.318.447-**', 'lucas.alves@email.example', 'E90817264202611081747A0000010450'),
    (10451, 6, '2026-11-08 20:11', 99900, 'Auto Peças Rota 66 Ltda', '56.789.012/0001-**', 'vendas@rota66.example', 'E90817264202611082011A0000010451'),
    (10452, 1, '2026-11-09 08:12', 240000, 'Imobiliária Nova Casa Ltda', '45.678.901/0001-**', 'aluguel@novacasa.example', 'E90817264202611090812A0000010452'),
    (10453, 4, '2026-11-09 11:50', 48900, 'Clínica Sorriso Odontologia', '34.567.890/0001-**', '+55 11 3****-2200', 'E90817264202611091150A0000010453'),
    (10454, 4, '2026-11-09 16:05', 12000, 'Beatriz Campos Nunes', '***.687.301-**', '+55 31 9****-1209', 'E90817264202611091605A0000010454'),
    (10455, 6, '2026-11-09 17:57', 189990, 'Thiago Moreira Lopes', '***.045.996-**', 'thiago.lopes@email.example', 'E90817264202611091757A0000010455'),
    (10456, 5, '2026-11-09 20:26', 48900, 'Escola Pequeno Saber Ltda', '23.456.789/0001-**', 'financeiro@pequenosaber.example', 'E90817264202611092026A0000010456'),
    (10457, 2, '2026-11-10 08:07', 89000, 'Clínica Sorriso Odontologia', '34.567.890/0001-**', '+55 11 3****-2200', 'E90817264202611100807A0000010457'),
    (10458, 1, '2026-11-10 11:50', 135000, 'Escola Pequeno Saber Ltda', '23.456.789/0001-**', 'financeiro@pequenosaber.example', 'E90817264202611101150A0000010458'),
    (10459, 6, '2026-11-10 16:10', 72015, 'Supermercado Bom Preço Ltda', '12.345.678/0001-**', 'pagamentos@bompreco.example', 'E90817264202611101610A0000010459'),
    (10460, 3, '2026-11-10 18:07', 25900, 'Auto Peças Rota 66 Ltda', '56.789.012/0001-**', 'vendas@rota66.example', 'E90817264202611101807A0000010460'),
]


def criar_banco(caminho: str) -> None:
    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(
            """
            DROP TABLE IF EXISTS pix_enviados;
            DROP TABLE IF EXISTS clientes;
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                documento TEXT NOT NULL,
                agencia TEXT NOT NULL,
                conta TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL
            );
            CREATE TABLE pix_enviados (
                id INTEGER PRIMARY KEY,
                cliente_id INTEGER NOT NULL REFERENCES clientes(id),
                data_hora TEXT NOT NULL,
                valor_centavos INTEGER NOT NULL,
                recebedor_nome TEXT NOT NULL,
                recebedor_documento TEXT NOT NULL,
                chave_pix TEXT NOT NULL,
                id_transacao TEXT NOT NULL
            );
            """
        )
        conexao.executemany(
            "INSERT INTO clientes VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (*dados, generate_password_hash(senha, method="pbkdf2:sha256:60000"))
                for *dados, senha in CLIENTES
            ],
        )
        conexao.executemany("INSERT INTO pix_enviados VALUES (?, ?, ?, ?, ?, ?, ?, ?)", PIX_ENVIADOS)
