"""Suíte da família graphql-bola (LAB-047..049) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa conferir, no resolver, que o pedido pertence ao usuário logado, e reprovar:
o código original (devolve o pedido só pelo id) e uma correção que só checa se o pedido existe, mas
não o dono (o pedido de outro usuário continua vazando).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import GRAPHQL_RAMOS, GraphqlRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-047-graphql-fintech", "lab-047-pedidos"),
    "sau": ("LAB-048-graphql-saude", "lab-048-pedidos"),
    "ind": ("LAB-049-graphql-industria", "lab-049-pedidos"),
}
SERVICO = "/workspace/services/pedido_service.py"

VULN = (
    "        # Devolve o pedido só pelo id, sem conferir se o dono é o usuário logado.\n"
    "        return self._repositorio.buscar(pedido_id)\n"
)
CORRETO = (
    "        # Confere o dono: só devolve o pedido se ele pertencer ao usuário logado.\n"
    "        pedido = self._repositorio.buscar(pedido_id)\n"
    "        if pedido is None or pedido.dono_id != usuario_id:\n"
    "            return None\n"
    "        return pedido\n"
)
# Só confere se o pedido existe, mas não o dono: o pedido de outro usuário continua vazando.
SO_EXISTENCIA = (
    "        pedido = self._repositorio.buscar(pedido_id)\n"
    "        if pedido is None:\n"
    "            return None\n"
    "        return pedido\n"
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
def test_original_code_leaks_other_users_object(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # O próprio pedido volta, mas o pedido de outro usuário não é negado: reprovado.
    assert r["proprio-ok"], r
    assert not r["de-outro-negado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_full_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_existence_check_only_still_leaks(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_EXISTENCIA)
    r = lab.evaluate(ev, ref)
    # Confere existência mas não o dono: o pedido de outro continua vazando: reprovado.
    assert r["proprio-ok"], r
    assert not r["de-outro-negado"], r


@pytest.mark.parametrize("r", GRAPHQL_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: GraphqlRamo) -> None:
    expected = {
        f"graphql-bola/answer/metodo-{r.ramo}-v1": "resolver",
        f"graphql-bola/answer/comportamento-{r.ramo}-v1": "devolve",
        f"graphql-bola/answer/defesa-{r.ramo}-v1": "dono",
        f"graphql-bola/answer/onde-{r.ramo}-v1": "não",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
