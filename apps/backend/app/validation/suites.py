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
    method: Literal["GET", "POST"] = "GET"
    form: dict[str, str] | None = None
    expect_status: int | None = 200
    contains: tuple[str, ...] = ()
    not_contains: tuple[str, ...] = ()


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

_SUITES = _SUITES + _SUITES_LAB001

REGISTRY: dict[str, Suite] = {s.ref: s for s in _SUITES}


def get_suite(ref: str) -> Suite | None:
    return REGISTRY.get(ref)
