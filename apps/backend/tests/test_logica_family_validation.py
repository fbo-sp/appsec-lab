"""Suíte da família logica-negocio (LAB-023..025) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa conferir, no servidor, que o valor do resgate é positivo e cabe no saldo, e reprovar:
o código original (debita qualquer valor), uma correção que só checa se o valor é positivo (deixa passar
acima do saldo) e uma que só checa o saldo (deixa passar valor negativo, que credita o usuário).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import LOGICA_RAMOS, LogicaRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-023-logica-cooperativa", "lab-023-logica"),
    "sau": ("LAB-024-logica-saude", "lab-024-logica"),
    "ind": ("LAB-025-logica-energia", "lab-025-logica"),
}
SERVICO = "/workspace/services/resgate_service.py"

VULN = (
    "        # Debita o valor pedido do saldo e devolve o saldo restante.\n"
    "        self._repositorio.debitar(conta_id, valor)\n"
    "        return conta.saldo - valor\n"
)
CORRETO = (
    "        if valor <= 0:\n"
    '            raise ValueError("O valor deve ser positivo.")\n'
    "        if valor > conta.saldo:\n"
    '            raise ValueError("Valor acima do saldo disponível.")\n'
    "        self._repositorio.debitar(conta_id, valor)\n"
    "        return conta.saldo - valor\n"
)
# Só confere se o valor é positivo: um resgate acima do saldo continua passando.
SO_POSITIVO = (
    "        if valor <= 0:\n"
    '            raise ValueError("O valor deve ser positivo.")\n'
    "        self._repositorio.debitar(conta_id, valor)\n"
    "        return conta.saldo - valor\n"
)
# Só confere o saldo: um valor negativo continua passando (e credita o usuário).
SO_SALDO = (
    "        if valor > conta.saldo:\n"
    '            raise ValueError("Valor acima do saldo disponível.")\n'
    "        self._repositorio.debitar(conta_id, valor)\n"
    "        return conta.saldo - valor\n"
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


def _lab(ramo: str) -> LabUnderTest:
    lab_dir, name = LABS[ramo]
    return LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_code_accepts_bad_values(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # Resgate legítimo funciona, mas acima do saldo e valor negativo não são recusados.
    assert r["resgate-legitimo"], r
    assert not r["acima-do-saldo-recusado"], r
    assert not r["valor-negativo-recusado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_full_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_only_positive_check_still_allows_over_balance(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_POSITIVO)
    r = lab.evaluate(ev, ref)
    # Barra o negativo, mas o resgate acima do saldo continua passando: reprovado.
    assert r["resgate-legitimo"] and r["valor-negativo-recusado"], r
    assert not r["acima-do-saldo-recusado"], r


def test_only_balance_check_still_allows_negative(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_SALDO)
    r = lab.evaluate(ev, ref)
    # Barra o acima do saldo, mas o valor negativo continua passando: reprovado.
    assert r["resgate-legitimo"] and r["acima-do-saldo-recusado"], r
    assert not r["valor-negativo-recusado"], r


@pytest.mark.parametrize("r", LOGICA_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: LogicaRamo) -> None:
    expected = {
        f"logica-negocio/answer/metodo-{r.ramo}-v1": "resgatar",
        f"logica-negocio/answer/aceito-{r.ramo}-v1": "aceito",
        f"logica-negocio/answer/limite-{r.ramo}-v1": "saldo",
        f"logica-negocio/answer/onde-{r.ramo}-v1": "servidor",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
