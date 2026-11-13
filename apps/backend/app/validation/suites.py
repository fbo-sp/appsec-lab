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

REGISTRY: dict[str, Suite] = {s.ref: s for s in _SUITES}


def get_suite(ref: str) -> Suite | None:
    return REGISTRY.get(ref)
