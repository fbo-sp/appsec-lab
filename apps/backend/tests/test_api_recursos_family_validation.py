"""Suíte da família api-recursos (LAB-074..076) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa prender o tamanho de página entre 1 e o teto, e reprovar: o código original (usa o
limite do cliente) e uma correção que só faz ``min(limite, teto)`` (o ``-1`` continua abrindo tudo,
porque no SQLite ``LIMIT -1`` é "sem limite").
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import RECURSOS_RAMOS, RecursosRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-074-api-recursos-banco", "lab-074-api-recursos", "lancamento"),
    "sau": ("LAB-075-api-recursos-saude", "lab-075-api-recursos", "atendimento"),
    "ind": ("LAB-076-api-recursos-industria", "lab-076-api-recursos", "leitura"),
}
VULN = "        deslocamento = max(pagina - 1, 0) * limite\n"
CORRETO = "        limite = max(1, min(limite, LIMITE_MAXIMO))\n" + VULN
SO_MIN = "        limite = min(limite, LIMITE_MAXIMO)\n" + VULN


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


def _avaliar(rt: Any, ev: Any, ramo: str, novo: str | None) -> dict[str, bool]:
    lab_dir, name, arquivo = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    box, ref = lab.provision(rt)
    try:
        if novo is not None:
            replace_in_file(box, f"/workspace/services/{arquivo}_service.py", VULN, novo)
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_returns_everything(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, None)
    assert r["pagina-normal"], r
    assert not r["limite-grande-contido"], r
    assert not r["limite-negativo-contido"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_clamped_page_size_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, CORRETO)
    assert all(r.values()), r


def test_only_min_still_lets_negative_through(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", SO_MIN)
    assert r["limite-grande-contido"], r
    assert not r["limite-negativo-contido"], r


@pytest.mark.parametrize("r", RECURSOS_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: RecursosRamo) -> None:
    expected = {
        f"api-recursos/answer/quantidade-{r.ramo}-v1": "20",
        f"api-recursos/answer/total-{r.ramo}-v1": str(r.total),
        f"api-recursos/answer/negativo-{r.ramo}-v1": "tudo",
        f"api-recursos/answer/metodo-{r.ramo}-v1": "listar",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
