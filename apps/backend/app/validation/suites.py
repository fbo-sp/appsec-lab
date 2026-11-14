"""Registro PROTEGIDO de suítes de validação (docs/10, docs/11 §3 regra 6).

Fica no plano de controle (imagem confiável) e nunca é montado no workspace do aluno. Respostas
esperadas e verificações não são expostas pela API; o aluno vê apenas a descrição pública de cada
critério e se passou.

Tipos:
- ``answer``: o aluno informa um valor observado no ambiente; comparação no backend.
- ``http``: verificações comportamentais contra uma CÓPIA isolada do workspace do aluno
  (snapshot), executadas por um probe confiável em rede efêmera própria (ADR-010).
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Literal


@dataclass(frozen=True, slots=True)
class HttpCheck:
    id: str
    description: str  # texto público mostrado ao aluno
    path: str
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"] = "GET"
    form: dict[str, str] | None = None
    expect_status: int | None = 200
    contains: tuple[str, ...] = ()
    not_contains: tuple[str, ...] = ()
    # ADR-015: verificações autenticadas e requisições de API.
    as_user: str | None = None  # nome de um HttpLogin da suíte; None = requisição anônima
    headers: dict[str, str] | None = None  # ex.: token forjado pela própria suíte
    json: dict[str, object] | None = None  # corpo JSON (alternativa a ``form``)
    expect_status_in: tuple[int, ...] = ()  # se informado, substitui ``expect_status``

    def to_probe(self) -> dict[str, object]:
        return {
            "id": self.id,
            "path": self.path,
            "method": self.method,
            "form": self.form,
            "json": self.json,
            "headers": self.headers,
            "expect_status": self.expect_status,
            "expect_status_in": list(self.expect_status_in),
            "contains": list(self.contains),
            "not_contains": list(self.not_contains),
            "as_user": self.as_user,
        }


@dataclass(frozen=True, slots=True)
class HttpLogin:
    """Sessão de um usuário FICTÍCIO do laboratório, aberta pelo probe antes das verificações (ADR-015)."""

    name: str
    path: str
    method: Literal["POST", "GET"] = "POST"
    form: dict[str, str] | None = None
    json: dict[str, object] | None = None
    token_field: str | None = None  # campo da resposta JSON usado como ``Authorization: Bearer``

    def to_probe(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AnswerSuite:
    ref: str
    version: str
    prompt: str  # rótulo público do campo de resposta
    accepted: tuple[str, ...]  # valores aceitos (normalizados na comparação)
    kind: Literal["answer"] = "answer"
    success_feedback: str = "Resposta correta."
    failure_feedback: str = "Resposta incorreta. Revise a tarefa e tente novamente."


@dataclass(frozen=True, slots=True)
class HttpSuite:
    ref: str
    version: str
    checks: tuple[HttpCheck, ...]
    kind: Literal["http"] = "http"
    timeout_seconds: int = 60
    success_feedback: str = "Todas as verificações passaram."
    failure_feedback: str = "Algumas verificações falharam. Ajuste o código e valide novamente."
    extra: dict[str, str] = field(default_factory=dict)
    logins: tuple[HttpLogin, ...] = ()

    def probe_checks(self) -> list[dict[str, object]]:
        return [c.to_probe() for c in self.checks]

    def probe_logins(self) -> list[dict[str, object]]:
        return [lg.to_probe() for lg in self.logins]


Suite = AnswerSuite | HttpSuite


def normalize_answer(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).strip().casefold()
    return re.sub(r"\s+", " ", text)[:200]


def suite_digest(suite: Suite) -> str:
    raw = json.dumps(asdict(suite), sort_keys=True, ensure_ascii=False, default=str).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


_SUITES: tuple[Suite, ...] = (
    # LAB-000 (benigno) ---------------------------------------------------------------------------
    AnswerSuite(
        ref="benign/answer/whoami-v1",
        version="1.0.0",
        prompt="Usuário que executa o terminal",
        accepted=("lab", "10001"),
        success_feedback="Isso mesmo: o workspace roda com um usuário sem privilégios de administrador.",
        failure_feedback="Não é esse. Use o terminal para descobrir o usuário atual.",
    ),
    HttpSuite(
        ref="benign/python-http/edit-page-v1",
        version="1.0.0",
        checks=(
            HttpCheck(
                id="page-greeting",
                description="A página inicial exibe o texto “Olá, CECyber”.",
                path="/",
                contains=("Olá, CECyber",),
            ),
            HttpCheck(
                id="page-still-served",
                description="A página continua sendo servida com sucesso (HTTP 200).",
                path="/index.html",
            ),
        ),
        success_feedback="Página atualizada e validada a partir de uma cópia isolada do seu workspace.",
    ),
)

# LAB-001 (SQL Injection, Clínica VidaPlena) ------------------------------------------------------
# Dados fictícios definidos em laboratories/LAB-001-sqli-clinica/runtime/workspace/database/seed.py.
_PACIENTE_EMAIL = "@pacientes.vidaplena.example"
_PACIENTE_CPF = "123.456.789-00"
_TOKEN = "VP-INT-7Q2K-93XD"  # noqa: S105 - valor FICTÍCIO do exercício, não é credencial
_SEM_RESULTADO = "Nenhum médico encontrado"

_SUITES_LAB001: tuple[Suite, ...] = (
    AnswerSuite(
        ref="sqli/answer/locate-query-v1",
        version="1.0.0",
        prompt="Nome do método que monta o SQL",
        accepted=(
            "buscar_por_nome",
            "buscar_por_nome()",
            "medicorepository.buscar_por_nome",
            "medicorepository.buscar_por_nome()",
        ),
        success_feedback="Isso: o repositório recebe o termo já limpo pelo serviço e o encaixa no SQL.",
        failure_feedback=(
            "Ainda não. Siga a busca a partir da rota /medicos até a camada que fala com o banco."
        ),
    ),
    AnswerSuite(
        ref="sqli/answer/error-type-v1",
        version="1.0.0",
        prompt="Tipo de erro registrado no log",
        accepted=("operationalerror", "sqlite3.operationalerror"),
        success_feedback="Exato: a aspa fechou o texto antes da hora e o banco recebeu um SQL inválido.",
        failure_feedback=(
            "Não é esse. Procure no log a linha final do erro, logo abaixo do caminho dos arquivos."
        ),
    ),
    AnswerSuite(
        ref="sqli/answer/column-count-v1",
        version="1.0.0",
        prompt="Número de colunas da consulta",
        accepted=("4", "quatro"),
        success_feedback="Isso: com 4 colunas você já consegue montar um UNION compatível.",
        failure_feedback="Não é esse número. Aumente o ORDER BY até o banco reclamar.",
    ),
    AnswerSuite(
        ref="sqli/answer/integration-token-v1",
        version="1.0.0",
        prompt="Token de integração encontrado",
        accepted=(_TOKEN.casefold(),),
        success_feedback="Você leu uma tabela que a busca nunca deveria mostrar. Agora vamos corrigir.",
        failure_feedback="Esse não é o token. Ele está na tabela configuracoes, na coluna valor.",
    ),
    HttpSuite(
        ref="sqli/python-flask/parameterized-search-v1",
        version="1.0.0",
        checks=(
            HttpCheck(
                id="busca-parcial",
                description="A busca por parte do nome continua encontrando o médico certo.",
                path="/medicos",
                method="POST",
                form={"nome": "Beatriz"},
                contains=("Ana Beatriz Souza",),
                not_contains=("Carlos Menezes",),
            ),
            HttpCheck(
                id="busca-vazia",
                description="A busca vazia continua listando todo o corpo clínico.",
                path="/medicos",
                method="POST",
                form={"nome": ""},
                contains=("Carlos Menezes", "Rafael Oliveira"),
            ),
            HttpCheck(
                id="apostrofo",
                description="Nomes com apóstrofo, como D'Ávila, continuam sendo encontrados.",
                path="/medicos",
                method="POST",
                form={"nome": "D'Ávila"},
                contains=("CRM-SP 123456",),
            ),
            HttpCheck(
                id="aspa-sem-erro",
                description="Uma aspa sozinha não causa erro no servidor.",
                path="/medicos",
                method="POST",
                form={"nome": "'"},
            ),
            HttpCheck(
                id="union-pacientes",
                description="Tentativas de UNION não revelam dados de pacientes.",
                path="/medicos",
                method="POST",
                form={"nome": "zz' UNION SELECT 1, email, cpf, condicao FROM pacientes --"},
                not_contains=(_PACIENTE_EMAIL, _PACIENTE_CPF),
            ),
            HttpCheck(
                id="union-configuracoes",
                description="Tentativas de UNION não revelam configurações internas.",
                path="/medicos",
                method="POST",
                form={"nome": "zz' UNION SELECT 1, valor, chave, valor FROM configuracoes --"},
                not_contains=(_TOKEN,),
            ),
            HttpCheck(
                id="condicao-injetada",
                description="Condições injetadas, como OR '1'='1', não alteram o resultado da busca.",
                path="/medicos",
                method="POST",
                form={"nome": "zz' OR '1'='1' --"},
                contains=(_SEM_RESULTADO,),
            ),
        ),
        success_feedback=(
            "Busca corrigida: os ataques viraram texto comum e as buscas legítimas continuam funcionando. "
            "Validado em uma cópia isolada do seu workspace."
        ),
        failure_feedback=(
            "Algumas verificações falharam. Confira cada item abaixo, ajuste o código e valide de novo."
        ),
    ),
)

# LAB-002 (IDOR, Banco Vértice Digital) ------------------------------------------------------------
# Dados e credenciais FICTÍCIOS: laboratories/LAB-002-idor-banco/runtime/workspace/database/seed.py.
_MARINA = HttpLogin(
    name="marina",
    path="/login",
    form={"email": "marina.ribeiro@clientes.vertice.example", "senha": "Marina@2026"},
)
_RODRIGO = HttpLogin(
    name="rodrigo",
    path="/login",
    form={"email": "rodrigo.lima@clientes.vertice.example", "senha": "Rodrigo@2026"},
)
_PIX_MARINA = "E90817264202611101150A0000010458"  # comprovante 10458 (Marina)
_PIX_RODRIGO = "E90817264202611100807A0000010457"  # comprovante 10457 (Rodrigo)
_RODRIGO_NOME = "Rodrigo Tavares Lima"
_NAO_ENCONTRADO = (403, 404)

_SUITES_LAB002: tuple[Suite, ...] = (
    AnswerSuite(
        ref="idor/answer/locate-lookup-v1",
        version="1.0.0",
        prompt="Nome do método do repositório",
        accepted=(
            "buscar_por_id",
            "buscar_por_id()",
            "comprovanterepository.buscar_por_id",
            "comprovanterepository.buscar_por_id()",
        ),
        success_feedback="Isso: o serviço busca o comprovante só pelo número. Guarde esse detalhe.",
        failure_feedback=(
            "Ainda não. Siga a rota /comprovantes/<comprovante_id> até a camada que fala com o banco."
        ),
    ),
    AnswerSuite(
        ref="idor/answer/latest-receipt-v1",
        version="1.0.0",
        prompt="Número do comprovante mais recente",
        accepted=("10458", "nº 10458", "n 10458"),
        success_feedback="Exato. Repare que os números são sequenciais: o vizinho provavelmente existe.",
        failure_feedback="Não é esse. Use o primeiro comprovante da lista, que é o mais recente.",
    ),
    AnswerSuite(
        ref="idor/answer/other-payer-v1",
        version="1.0.0",
        prompt="Nome do pagador do comprovante 10457",
        accepted=(_RODRIGO_NOME.casefold(),),
        success_feedback="Você leu o comprovante de outro cliente só trocando um número. Isso é um IDOR.",
        failure_feedback="Não é esse nome. Abra /comprovantes/10457 e veja a seção Pagador.",
    ),
    AnswerSuite(
        ref="idor/answer/leaked-count-v1",
        version="1.0.0",
        prompt="Comprovantes de outros clientes",
        accepted=("34", "trinta e quatro"),
        success_feedback="Isso: 34 comprovantes de outros clientes em poucos segundos. Agora vamos corrigir.",
        failure_feedback="Não é esse número. Confira o login do curl e conte as linhas sem o nome da Marina.",
    ),
    HttpSuite(
        ref="idor/python-flask/owner-check-v1",
        version="1.0.0",
        logins=(_MARINA, _RODRIGO),
        checks=(
            HttpCheck(
                id="proprio-comprovante",
                description="A Marina continua vendo o próprio comprovante na página.",
                path="/comprovantes/10458",
                as_user="marina",
                contains=("Escola Pequeno Saber Ltda", "R$ 1.350,00"),
            ),
            HttpCheck(
                id="propria-api",
                description="A Marina continua vendo o próprio comprovante pela API.",
                path="/api/comprovantes/10458",
                as_user="marina",
                contains=(_PIX_MARINA,),
            ),
            HttpCheck(
                id="lista-propria",
                description="A lista de comprovantes da Marina continua funcionando.",
                path="/comprovantes",
                as_user="marina",
                contains=("10458", "Imobiliária Nova Casa Ltda"),
            ),
            HttpCheck(
                id="outro-cliente-pagina",
                description="A página não mostra à Marina o comprovante de outro cliente.",
                path="/comprovantes/10457",
                as_user="marina",
                expect_status=None,
                not_contains=(_RODRIGO_NOME, _PIX_RODRIGO),
            ),
            HttpCheck(
                id="outro-cliente-api",
                description="A API responde 404 (ou 403) quando a Marina pede o comprovante de outra pessoa.",
                path="/api/comprovantes/10457",
                as_user="marina",
                expect_status_in=_NAO_ENCONTRADO,
                not_contains=(_RODRIGO_NOME, _PIX_RODRIGO),
            ),
            HttpCheck(
                id="parametro-forjado",
                description="Informar o id de outro cliente na URL (?cliente_id=2) não libera o comprovante.",
                path="/api/comprovantes/10457?cliente_id=2",
                as_user="marina",
                expect_status_in=_NAO_ENCONTRADO,
                not_contains=(_RODRIGO_NOME, _PIX_RODRIGO),
            ),
            HttpCheck(
                id="dono-ve-o-seu",
                description="O Rodrigo, dono do comprovante 10457, continua conseguindo vê-lo.",
                path="/api/comprovantes/10457",
                as_user="rodrigo",
                contains=(_PIX_RODRIGO,),
            ),
            HttpCheck(
                id="sem-login",
                description="Sem login, a API não entrega comprovantes.",
                path="/api/comprovantes/10458",
                expect_status=None,
                not_contains=(_PIX_MARINA,),
            ),
        ),
        success_feedback=(
            "Comprovantes protegidos: cada cliente só vê os próprios, na página e na API. "
            "Validado em uma cópia isolada do seu workspace, com dois clientes fictícios."
        ),
        failure_feedback=(
            "Algumas verificações falharam. Confira cada item abaixo, ajuste o código e valide de novo."
        ),
    ),
)

# LAB-003 (JWT, Orbe Cartões) ------------------------------------------------------------------------
# Dados e credenciais FICTÍCIOS: laboratories/LAB-003-jwt-cartoes/runtime/workspace/data/seed.js.
# Tokens forjados pela suíte (todos com perfil admin, exceto o expirado):
_JWT_SEM_ASSINATURA = (  # alg "none", sem assinatura
    "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOjEsIm5vbWUiOiJMYXJpc3NhIE1lbmRlcyIsInBlcmZpbCI6ImFkbWluIn0."
)
_JWT_OUTRA_CHAVE = (  # HS256 assinado com "chave-do-atacante"
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsIm5vbWUiOiJMYXJpc3NhIE1lbmRlcyIsInBlcmZpbCI6ImFkbWlu"
    "IiwiaWF0IjoxNzk0NjAwMDAwLCJleHAiOjQxMDI0NDQ4MDB9.KzGIY-CLvPHCTq6e2KKVlllTSWCRC31mPYiO9-kiDn0"
)
_JWT_ADULTERADO = (  # assinatura legítima de um token "cliente" com o perfil trocado para "admin"
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsIm5vbWUiOiJMYXJpc3NhIE1lbmRlcyIsInBlcmZpbCI6ImFkbWlu"
    "IiwiaWF0IjoxNzk0NjAwMDAwLCJleHAiOjQxMDI0NDQ4MDB9.5-l3lVBlP24_7VQBoIxl0vRe4HRFNkpDJSK4Xh0lpUU"
)
_JWT_EXPIRADO = (  # segredo correto do laboratório, perfil cliente, expirado em 2023
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsIm5vbWUiOiJMYXJpc3NhIE1lbmRlcyIsInBlcmZpbCI6ImNsaWVu"
    "dGUiLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDAwMTgwMH0.Jl_TNzMj6yZBOcIQS2cIqTRr1S_Yr9ROdHCIImsCmB8"
)
_AUDITORIA = "ORB-AUD-5583-QX"
_RECUSADO = (401, 403)


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


_SUITES_LAB003: tuple[Suite, ...] = (
    AnswerSuite(
        ref="jwt/answer/locate-reader-v1",
        version="1.0.0",
        prompt="Nome da função que lê o token",
        accepted=("lertoken", "lertoken()", "tokenservice.lertoken", "token.service.lertoken"),
        success_feedback="Isso: toda rota protegida depende do que essa função devolve.",
        failure_feedback="Ainda não. Abra middlewares/autenticacao.js e veja qual função recebe o token.",
    ),
    AnswerSuite(
        ref="jwt/answer/profile-claim-v1",
        version="1.0.0",
        prompt="Valor do campo perfil no token",
        accepted=("cliente", '"cliente"'),
        success_feedback="Exato. Qualquer um lê o conteúdo de um JWT: ele é codificado, não criptografado.",
        failure_feedback="Não é esse. Decodifique a parte do meio do token e procure o campo perfil.",
    ),
    AnswerSuite(
        ref="jwt/answer/audit-code-v1",
        version="1.0.0",
        prompt="Código de auditoria do painel",
        accepted=(_AUDITORIA.casefold(),),
        success_feedback="Você entrou no painel do gerente com um token que você mesmo escreveu.",
        failure_feedback="Esse não é o código. Ele vem no campo codigoAuditoria de /api/admin/resumo.",
    ),
    AnswerSuite(
        ref="jwt/answer/limit-protocol-v1",
        version="1.0.0",
        prompt="Protocolo da alteração de limite",
        accepted=("orb-lim-4821-50000",),
        success_feedback="Limite aumentado sem análise de crédito. Agora vamos corrigir a validação.",
        failure_feedback="Não é esse protocolo. Use o cartão de id 1 e o novo limite 50000, como na tarefa.",
    ),
    HttpSuite(
        ref="jwt/node-express/verify-signature-v1",
        version="1.0.0",
        logins=(
            HttpLogin(
                name="larissa",
                path="/api/login",
                json={"email": "larissa.mendes@clientes.orbe.example", "senha": "Larissa@2026"},
                token_field="token",  # noqa: S106 - nome do campo JSON, não é senha
            ),
            HttpLogin(
                name="gerente",
                path="/api/login",
                json={"email": "helena.castro@orbe.example", "senha": "Gerente#Credito2026"},
                token_field="token",  # noqa: S106 - nome do campo JSON, não é senha
            ),
        ),
        checks=(
            HttpCheck(
                id="cliente-ve-cartao",
                description="Com um token legítimo, a cliente continua vendo o próprio cartão.",
                path="/api/cartoes/meu",
                as_user="larissa",
                contains=("4821",),
            ),
            HttpCheck(
                id="gerente-ve-painel",
                description="O gerente, com token legítimo, continua acessando o painel.",
                path="/api/admin/resumo",
                as_user="gerente",
                contains=(_AUDITORIA,),
            ),
            HttpCheck(
                id="cliente-nao-e-gerente",
                description="Com o próprio token, a cliente continua sem acesso ao painel (403).",
                path="/api/admin/resumo",
                as_user="larissa",
                expect_status=403,
                not_contains=(_AUDITORIA,),
            ),
            HttpCheck(
                id="sem-assinatura",
                description='Um token com alg "none" e sem assinatura é recusado.',
                path="/api/admin/resumo",
                headers=_bearer(_JWT_SEM_ASSINATURA),
                expect_status_in=_RECUSADO,
                not_contains=(_AUDITORIA,),
            ),
            HttpCheck(
                id="outra-chave",
                description="Um token assinado com outra chave é recusado.",
                path="/api/admin/resumo",
                headers=_bearer(_JWT_OUTRA_CHAVE),
                expect_status_in=_RECUSADO,
                not_contains=(_AUDITORIA,),
            ),
            HttpCheck(
                id="token-adulterado",
                description="Um token legítimo com o perfil trocado para admin é recusado.",
                path="/api/admin/resumo",
                headers=_bearer(_JWT_ADULTERADO),
                expect_status_in=_RECUSADO,
                not_contains=(_AUDITORIA,),
            ),
            HttpCheck(
                id="token-expirado",
                description="Um token expirado é recusado (401).",
                path="/api/cartoes/meu",
                headers=_bearer(_JWT_EXPIRADO),
                expect_status=401,
                not_contains=("4821",),
            ),
            HttpCheck(
                id="limite-forjado",
                description="Não é possível alterar limite com token forjado.",
                path="/api/admin/cartoes/1/limite",
                method="PATCH",
                json={"novoLimite": 50000},
                headers=_bearer(_JWT_SEM_ASSINATURA),
                expect_status_in=_RECUSADO,
                not_contains=("ORB-LIM-",),
            ),
        ),
        success_feedback=(
            "Tokens validados: assinatura, algoritmo e validade são conferidos antes de confiar no perfil. "
            "Validado em uma cópia isolada do seu workspace."
        ),
        failure_feedback=(
            "Algumas verificações falharam. Confira cada item abaixo, ajuste o código e valide de novo."
        ),
    ),
)

# LAB-004 (OS Command Injection, Ferrara Metais) -----------------------------------------------------
# CLPs simulados e arquivos FICTÍCIOS: laboratories/LAB-004-cmdi-industria/runtime/planta/.
# Cada ataque imprime um marcador montado pelo próprio shell (printf 'CMD%sOK' X => CMDXOK), que só
# aparece na resposta se o comando for EXECUTADO; o texto enviado nunca contém o marcador pronto.
_SENHA_SCADA = "SCADA-OPR-4471-KX"


def _injecao(check_id: str, descricao: str, entrada: str, marcador: str) -> HttpCheck:
    return HttpCheck(
        id=check_id,
        description=descricao,
        path="/diagnostico",
        method="POST",
        form={"endereco": entrada},
        expect_status=None,
        not_contains=(marcador,),
    )


_SUITES_LAB004: tuple[Suite, ...] = (
    AnswerSuite(
        ref="cmdi/answer/locate-program-v1",
        version="1.0.0",
        prompt="Nome do programa executado",
        accepted=("diag-clp", "/usr/local/bin/diag-clp"),
        success_feedback="Isso: o endereço digitado é colado logo depois do nome do programa.",
        failure_feedback="Ainda não. Procure onde o comando é montado em services/diagnostico_service.py.",
    ),
    AnswerSuite(
        ref="cmdi/answer/process-user-v1",
        version="1.0.0",
        prompt="Usuário que executou o comando",
        accepted=("lab", "10001"),
        success_feedback="Exato: você executou um comando seu no servidor, com o usuário da aplicação.",
        failure_feedback="Não é esse. Veja a última linha do resultado do teste com ; whoami.",
    ),
    AnswerSuite(
        ref="cmdi/answer/scada-file-v1",
        version="1.0.0",
        prompt="Arquivo de configuração do SCADA",
        accepted=("scada.conf", "/opt/planta/scada.conf"),
        success_feedback="Isso: a configuração de um sistema industrial ao alcance da aplicação web.",
        failure_feedback="Não é esse. Liste /opt/planta e procure o arquivo .conf.",
    ),
    AnswerSuite(
        ref="cmdi/answer/scada-password-v1",
        version="1.0.0",
        prompt="Senha do operador do SCADA",
        accepted=(_SENHA_SCADA.casefold(),),
        success_feedback="Você leu uma credencial do supervisório pela página web. Agora vamos corrigir.",
        failure_feedback="Essa não é a senha. Ela está na linha senha_operador do scada.conf.",
    ),
    HttpSuite(
        ref="cmdi/python-flask/no-shell-v1",
        version="1.0.0",
        checks=(
            HttpCheck(
                id="clp-responde",
                description="O teste de um CLP cadastrado (10.20.1.15) continua funcionando.",
                path="/diagnostico",
                method="POST",
                form={"endereco": "10.20.1.15"},
                contains=("CLP Prensa Hidráulica 02", "status=OK"),
            ),
            HttpCheck(
                id="clp-sem-resposta",
                description="Um endereço válido sem CLP (10.20.1.99) continua sendo testado.",
                path="/diagnostico",
                method="POST",
                form={"endereco": "10.20.1.99"},
                contains=("sem resposta",),
            ),
            HttpCheck(
                id="ponto-e-virgula",
                description="Comandos encadeados com ; não leem o scada.conf.",
                path="/diagnostico",
                method="POST",
                form={"endereco": "10.20.1.15; cat /opt/planta/scada.conf"},
                expect_status=None,
                not_contains=(_SENHA_SCADA,),
            ),
            _injecao(
                "e-comercial",
                "Comandos encadeados com && não são executados.",
                "10.20.1.15 && printf 'CMD%sOK' -E1-",
                "CMD-E1-OK",
            ),
            _injecao(
                "pipe",
                "Comandos com | (pipe) não são executados.",
                "10.20.1.15 | printf 'CMD%sOK' -P1-",
                "CMD-P1-OK",
            ),
            _injecao(
                "ou-logico",
                "Comandos com || não são executados.",
                "10.20.1.99 || printf 'CMD%sOK' -O1-",
                "CMD-O1-OK",
            ),
            _injecao(
                "subshell",
                "Comandos dentro de $( ) não são executados.",
                "$(printf 'CMD%sOK' -S1-)",
                "CMD-S1-OK",
            ),
            _injecao(
                "crase", "Comandos entre crases não são executados.", "`printf 'CMD%sOK' -C1-`", "CMD-C1-OK"
            ),
            _injecao(
                "quebra-de-linha",
                "Comandos após uma quebra de linha não são executados.",
                "10.20.1.15\nprintf 'CMD%sOK' -N1-",
                "CMD-N1-OK",
            ),
        ),
        success_feedback=(
            "Teste de comunicação corrigido: nenhum metacaractere virou comando e os CLPs continuam "
            "respondendo. Validado em uma cópia isolada do seu workspace."
        ),
        failure_feedback=(
            "Algumas verificações falharam. Confira cada item abaixo, ajuste o código e valide de novo."
        ),
    ),
)

_SUITES = _SUITES + _SUITES_LAB001 + _SUITES_LAB002 + _SUITES_LAB003 + _SUITES_LAB004

REGISTRY: dict[str, Suite] = {s.ref: s for s in _SUITES}


def get_suite(ref: str) -> Suite | None:
    return REGISTRY.get(ref)
