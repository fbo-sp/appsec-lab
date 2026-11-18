"""Suíte da família api-inventario (LAB-068..070) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa impedir que a v1 legada entregue documentos de outra conta, e reprovar: o código
original (v1 sem conferir o dono) e uma correção que só esconde o campo ``titular`` (o detalhe do
documento alheio continua saindo).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import INVENTARIO_RAMOS, InventarioRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-068-api-inventario-banco", "lab-068-api-inventario"),
    "sau": ("LAB-069-api-inventario-saude", "lab-069-api-inventario"),
    "ind": ("LAB-070-api-inventario-industria", "lab-070-api-inventario"),
}
V1 = "/workspace/controllers/api_v1_controller.py"

VULN = (
    '    """Versão 1 (legada): devolve o documento pelo id, de qualquer conta."""\n'
    '    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:\n'
    "        documento = DocumentoRepository(conexao).buscar(doc_id)\n"
    "    if documento is None:\n"
    '        return jsonify({"erro": "não encontrado"}), 404\n'
    "    return jsonify(documento.como_dict())\n"
)
APOSENTADA = (
    '    """Versão 1 (legada): desativada. Os apps devem usar a v2."""\n'
    '    return jsonify({"erro": "versão desativada; use /api/v2"}), 410\n'
)
# Correção ingênua: tira só o nome do titular; o documento alheio continua saindo.
SO_ESCONDE_TITULAR = VULN.replace(
    "    return jsonify(documento.como_dict())\n",
    '    dados = documento.como_dict()\n    dados.pop("titular")\n    return jsonify(dados)\n',
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


def _avaliar(rt: Any, ev: Any, ramo: str, novo: str | None) -> dict[str, bool]:
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    try:
        if novo is not None:
            replace_in_file(box, V1, VULN, novo)
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_v1_leaks_other_account(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, None)
    assert r["v2-continua"] and r["v2-protege"], r
    assert not r["v1-nao-vaza"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_retiring_v1_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, APOSENTADA)
    assert all(r.values()), r


def test_hiding_only_the_owner_name_still_fails(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", SO_ESCONDE_TITULAR)
    assert not r["v1-nao-vaza"], r


@pytest.mark.parametrize("r", INVENTARIO_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: InventarioRamo) -> None:
    expected = {
        f"api-inventario/answer/versao-{r.ramo}-v1": "v2",
        f"api-inventario/answer/arquivo-{r.ramo}-v1": "api_v1_controller.py",
        f"api-inventario/answer/titular-{r.ramo}-v1": r.nome_b,
        f"api-inventario/answer/conceito-{r.ramo}-v1": "inventário",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
