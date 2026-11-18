"""Suíte da família cookie-transporte (LAB-086..088) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção liga Secure, HttpOnly e SameSite no cookie de sessão e acrescenta o HSTS, e a suíte (que lê o
Set-Cookie da resposta 302 do login, ADR-027) reprova: o código original (sem nenhuma proteção) e uma
correção parcial que só liga o HttpOnly.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import COOKIE_RAMOS, CookieRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-086-cookie-transporte-banco", "lab-086-cookie-transporte"),
    "sau": ("LAB-087-cookie-transporte-saude", "lab-087-cookie-transporte"),
    "ind": ("LAB-088-cookie-transporte-industria", "lab-088-cookie-transporte"),
}
ARQUIVO = "/workspace/config.py"
FLAGS = (
    "    SESSION_COOKIE_SECURE = False\n"
    '    SESSION_COOKIE_HTTPONLY = False  # o antigo aviso de "sessão expirando" lia o cookie pelo JavaScript\n'
    "    SESSION_COOKIE_SAMESITE = None\n"
)
FLAGS_OK = '    SESSION_COOKIE_SECURE = True\n    SESSION_COOKIE_HTTPONLY = True\n    SESSION_COOKIE_SAMESITE = "Lax"\n'
SO_HTTPONLY = "    SESSION_COOKIE_SECURE = False\n    SESSION_COOKIE_HTTPONLY = True\n    SESSION_COOKIE_SAMESITE = None\n"
HEADERS = '        "Referrer-Policy": "same-origin",\n    }'
HEADERS_OK = (
    '        "Referrer-Policy": "same-origin",\n'
    '        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",\n    }'
)


@pytest.fixture(scope="module")
def runtime() -> Iterator[tuple[Any, Any]]:
    docker_lab_image()  # pula sem DOCKER_CONTRACT_TESTS=1 antes de tocar no Docker
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    before = {owned.runtime_ref for owned in rt.list_owned()}  # não derruba sessões de outra pilha local
    try:
        yield rt, DockerEvaluator()
    finally:
        for owned in rt.list_owned():
            if owned.runtime_ref not in before:
                rt.terminate(owned.runtime_ref)


def _avaliar(rt: Any, ev: Any, ramo: str, trocas: tuple[tuple[str, str], ...]) -> dict[str, bool]:
    lab_dir, name = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    box, ref = lab.provision(rt)
    try:
        for old, new in trocas:
            replace_in_file(box, ARQUIVO, old, new)
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_cookie_has_no_protection(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, ())
    assert r["login-continua"], r
    assert not r["cookie-secure"] and not r["cookie-httponly"] and not r["cookie-samesite"], r
    assert not r["hsts"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_flags_and_hsts_pass(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, ((FLAGS, FLAGS_OK), (HEADERS, HEADERS_OK)))
    assert all(r.values()), r


def test_only_httponly_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", ((FLAGS, SO_HTTPONLY),))
    assert r["cookie-httponly"], r
    assert not r["cookie-secure"] and not r["hsts"], r


@pytest.mark.parametrize("r", COOKIE_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: CookieRamo) -> None:
    expected = {
        f"cookie-transporte/answer/nome-{r.ramo}-v1": "session",
        f"cookie-transporte/answer/flags-{r.ramo}-v1": "0",
        f"cookie-transporte/answer/hsts-{r.ramo}-v1": "Strict-Transport-Security",
        f"cookie-transporte/answer/arquivo-{r.ramo}-v1": "config.py",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
