"""Suíte da família componente-desatualizado (LAB-080..082) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção é atualizar a relatorix (biblioteca FICTÍCIA do espelho interno) para a 2.4.1 em
requirements.txt, e a suíte reprova: o código original (2.1.0 abre modelos fora da pasta) e um filtro
de texto no serviço, que barra ``..`` e ``/`` mas deixa passar a forma codificada que a biblioteca
decodifica sozinha.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import COMPONENTE_RAMOS, ComponenteRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-080-componente-desatualizado-banco", "lab-080-componente-desatualizado"),
    "sau": ("LAB-081-componente-desatualizado-saude", "lab-081-componente-desatualizado"),
    "ind": ("LAB-082-componente-desatualizado-industria", "lab-082-componente-desatualizado"),
}
DOC = '        """Preenche o modelo escolhido com os dados da conta e devolve o HTML do documento."""\n'
FILTRO = (
    DOC
    + '        if ".." in modelo or modelo.startswith("/"):\n            raise ValueError("Modelo inválido.")\n'
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


def _avaliar(rt: Any, ev: Any, ramo: str, patch: tuple[str, str, str] | None) -> dict[str, bool]:
    lab_dir, name = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    box, ref = lab.provision(rt)
    try:
        if patch is not None:
            replace_in_file(box, *patch)
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_reads_outside_templates(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, None)
    assert r["documento-padrao"], r
    assert not r["modelo-fora-da-pasta"], r
    assert not r["modelo-codificado"], r
    assert not r["caminho-absoluto"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_upgraded_dependency_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, ("/workspace/requirements.txt", "relatorix==2.1.0", "relatorix==2.4.1"))
    assert all(r.values()), r


def test_text_filter_misses_encoded_name(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", ("/workspace/services/documento_service.py", DOC, FILTRO))
    assert r["modelo-fora-da-pasta"], r
    assert r["caminho-absoluto"], r
    assert not r["modelo-codificado"], r


@pytest.mark.parametrize("r", COMPONENTE_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: ComponenteRamo) -> None:
    expected = {
        f"componente-desatualizado/answer/versao-{r.ramo}-v1": "2.1.0",
        f"componente-desatualizado/answer/corrigida-{r.ramo}-v1": "2.4.1",
        f"componente-desatualizado/answer/marcador-{r.ramo}-v1": "INTEGRACOES-DEMO",
        f"componente-desatualizado/answer/arquivo-{r.ramo}-v1": "requirements.txt",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
