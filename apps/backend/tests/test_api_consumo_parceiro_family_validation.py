"""Suíte da família api-consumo-parceiro (LAB-071..073) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa recusar a resposta do parceiro fora do contrato e decidir o status do lado do app,
e reprovar: o código original (grava o que vier) e uma correção que só limita o valor ao teto (o campo
fora do contrato continua aprovando a consulta).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import CONSUMO_RAMOS, ConsumoRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-071-api-consumo-parceiro-banco", "lab-071-api-consumo", "limite_sugerido", 50000),
    "sau": ("LAB-072-api-consumo-parceiro-saude", "lab-072-api-consumo", "valor_reembolso", 20000),
    "ind": ("LAB-073-api-consumo-parceiro-industria", "lab-073-api-consumo", "preco_unitario", 10000),
}
SERVICO = "/workspace/services/consulta_service.py"


def _vuln(campo: str) -> str:
    return (
        '        """Grava a resposta do parceiro como veio."""\n'
        f'        valor = dados["{campo}"]\n'
        '        status = "aprovado" if dados.get("aprovacao_automatica") else "em análise"\n'
        "        return self._repositorio.inserir(conta_id, referencia, valor, status)\n"
    )


def _correto(campo: str, teto: int) -> str:
    return (
        '        """Confere o contrato da resposta antes de gravar; o status é decisão nossa."""\n'
        f'        if set(dados) != {{"referencia", "{campo}"}}:\n'
        '            raise RespostaInvalida("campos fora do contrato")\n'
        f'        valor = dados["{campo}"]\n'
        f"        if not isinstance(valor, (int, float)) or not 0 <= valor <= {teto}:\n"
        '            raise RespostaInvalida("valor fora da faixa")\n'
        '        return self._repositorio.inserir(conta_id, referencia, valor, "em análise")\n'
    )


def _so_limita(campo: str, teto: int) -> str:
    """Correção ingênua: corta o valor no teto, mas o campo fora do contrato ainda aprova."""
    return _vuln(campo).replace(f'valor = dados["{campo}"]', f'valor = min(dados["{campo}"], {teto})')


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


def _avaliar(rt: Any, ev: Any, ramo: str, fix: str | None) -> dict[str, bool]:
    lab_dir, name, campo, teto = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    box, ref = lab.provision(rt)
    try:
        if fix == "correto":
            replace_in_file(box, SERVICO, _vuln(campo), _correto(campo, teto))
        elif fix == "so_limita":
            replace_in_file(box, SERVICO, _vuln(campo), _so_limita(campo, teto))
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_accepts_tampered_partner_response(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, None)
    assert r["consulta-normal-gravada"], r
    assert not r["resposta-adulterada-recusada"], r
    assert not r["status-decidido-pelo-app"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_contract_check_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, "correto")
    assert all(r.values()), r


def test_only_clamping_the_value_still_fails(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", "so_limita")
    assert not r["resposta-adulterada-recusada"], r
    assert not r["status-decidido-pelo-app"], r


@pytest.mark.parametrize("r", CONSUMO_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: ConsumoRamo) -> None:
    expected = {
        f"api-consumo-parceiro/answer/cliente-{r.ramo}-v1": "parceiro_client.py",
        f"api-consumo-parceiro/answer/status-{r.ramo}-v1": "aprovado",
        f"api-consumo-parceiro/answer/contrato-{r.ramo}-v1": "contrato",
        f"api-consumo-parceiro/answer/metodo-{r.ramo}-v1": "registrar",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
