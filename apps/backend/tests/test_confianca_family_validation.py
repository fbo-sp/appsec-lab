"""Suíte da família confianca-cliente (LAB-035..037) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa cobrar o custo REAL do produto (do banco), ignorando o custo do formulário, e
reprovar: o código original (debita o custo do formulário) e uma correção que só confere se o custo
informado é positivo mas ainda o debita (custo=1 continua passando).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import CONFIANCA_RAMOS, ConfiancaRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-035-confianca-cooperativa", "lab-035-confianca"),
    "sau": ("LAB-036-confianca-saude", "lab-036-confianca"),
    "ind": ("LAB-037-confianca-energia", "lab-037-confianca"),
}
SERVICO = "/workspace/services/loja_service.py"

VULN = (
    "    def resgatar(self, conta_id: int, produto_id: int, custo_informado: int) -> float:\n"
    '        """Resgata o produto para a conta e devolve o novo saldo de pontos."""\n'
    "        conta = self._contas.buscar(conta_id)\n"
    "        if conta is None:\n"
    '            raise ValueError("Conta não encontrada.")\n'
    "        produto = self._produtos.buscar(produto_id)\n"
    "        if produto is None:\n"
    '            raise ValueError("Produto não encontrado.")\n'
    "        # Usa o custo que veio do formulário, sem conferir com o custo real do produto no banco.\n"
    "        self._contas.debitar(conta_id, custo_informado)\n"
    "        return conta.saldo - custo_informado\n"
)
CORRETO = (
    "    def resgatar(self, conta_id: int, produto_id: int, custo_informado: int) -> float:\n"
    '        """Resgata o produto para a conta e devolve o novo saldo de pontos."""\n'
    "        conta = self._contas.buscar(conta_id)\n"
    "        if conta is None:\n"
    '            raise ValueError("Conta não encontrada.")\n'
    "        produto = self._produtos.buscar(produto_id)\n"
    "        if produto is None:\n"
    '            raise ValueError("Produto não encontrado.")\n'
    "        # O custo é o do produto no banco; o valor do formulário é ignorado.\n"
    "        if produto.custo > conta.saldo:\n"
    '            raise ValueError("Saldo de pontos insuficiente.")\n'
    "        self._contas.debitar(conta_id, produto.custo)\n"
    "        return conta.saldo - produto.custo\n"
)
# Só confere se o custo informado é positivo, mas continua debitando o custo do formulário.
SO_POSITIVO = (
    "    def resgatar(self, conta_id: int, produto_id: int, custo_informado: int) -> float:\n"
    '        """Resgata o produto para a conta e devolve o novo saldo de pontos."""\n'
    "        conta = self._contas.buscar(conta_id)\n"
    "        if conta is None:\n"
    '            raise ValueError("Conta não encontrada.")\n'
    "        produto = self._produtos.buscar(produto_id)\n"
    "        if produto is None:\n"
    '            raise ValueError("Produto não encontrado.")\n'
    "        if custo_informado <= 0:\n"
    '            raise ValueError("Custo inválido.")\n'
    "        self._contas.debitar(conta_id, custo_informado)\n"
    "        return conta.saldo - custo_informado\n"
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
def test_original_code_trusts_client_cost(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # Catálogo visível, mas o custo adulterado (1) é aceito: o custo real (300) não foi cobrado.
    assert r["catalogo-visivel"], r
    assert not r["custo-real-cobrado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_server_cost_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_only_positive_check_still_trusts_client_cost(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_POSITIVO)
    r = lab.evaluate(ev, ref)
    # Custo positivo, mas ainda é o do formulário: custo=1 continua passando. Reprovado.
    assert not r["custo-real-cobrado"], r


@pytest.mark.parametrize("r", CONFIANCA_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: ConfiancaRamo) -> None:
    expected = {
        f"confianca-cliente/answer/metodo-{r.ramo}-v1": "resgatar",
        f"confianca-cliente/answer/quem-define-{r.ramo}-v1": "loja",
        f"confianca-cliente/answer/vem-de-onde-{r.ramo}-v1": "banco",
        f"confianca-cliente/answer/confiar-{r.ramo}-v1": "não",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
