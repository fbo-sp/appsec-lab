"""Suíte da família mob-token-url (LAB-095..097) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção faz ``IdentidadeService.identificar`` aceitar o token só no cabeçalho ``Authorization`` e
recusar qualquer pedido com ``?token=``, e desliga ``token_na_url`` no ``cliente/config.json``. A suíte
reprova: o código original, a correção só no app (o servidor ainda aceita o token do log) e a correção
só no servidor (o app continua configurado para vazar o token).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import TOKENURL_RAMOS, TokenUrlRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-095-mob-token-url-fintech", "lab-095-mobile"),
    "sau": ("LAB-096-mob-token-url-saude", "lab-096-mobile"),
    "ind": ("LAB-097-mob-token-url-industria", "lab-097-mobile"),
}
SERVICO = "/workspace/services/identidade_service.py"
CONFIG = "/workspace/cliente/config.json"
VULN = 'token = token_cabecalho or parametros.get("token")\n        return self._tokens.conta_do_token(token) if token else None'
CORRIGIDO = (
    'if "token" in parametros:\n'
    "            return None\n"
    "        return self._tokens.conta_do_token(token_cabecalho) if token_cabecalho else None"
)
CORRECAO_SERVIDOR = ((SERVICO, VULN, CORRIGIDO),)
CORRECAO_APP = ((CONFIG, '"token_na_url": true', '"token_na_url": false'),)


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


def _avaliar(rt: Any, ev: Any, ramo: str, trocas: tuple[tuple[str, str, str], ...]) -> dict[str, bool]:
    lab_dir, name = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    box, ref = lab.provision(rt)
    try:
        for arquivo, old, new in trocas:
            replace_in_file(box, arquivo, old, new)
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_accepts_token_in_url(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, ())
    assert r["cabecalho-funciona"], r
    assert not r["token-na-url-recusado"], r
    assert not r["app-sem-token-na-url"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_header_only_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, CORRECAO_SERVIDOR + CORRECAO_APP)
    assert all(r.values()), r


def test_app_only_fix_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", CORRECAO_APP)
    assert r["app-sem-token-na-url"], r
    assert not r["token-na-url-recusado"], r


def test_server_only_fix_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", CORRECAO_SERVIDOR)
    assert r["token-na-url-recusado"], r
    assert not r["app-sem-token-na-url"], r


@pytest.mark.parametrize("r", TOKENURL_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: TokenUrlRamo) -> None:
    expected = {
        f"mob-token-url/answer/config-{r.ramo}-v1": "true",
        f"mob-token-url/answer/reuso-{r.ramo}-v1": "sim",
        f"mob-token-url/answer/cabecalho-{r.ramo}-v1": "Authorization",
        f"mob-token-url/answer/metodo-{r.ramo}-v1": "identificar",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
