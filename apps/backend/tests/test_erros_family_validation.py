"""Suíte da família erros-verbosos (LAB-041..043) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa responder a erros com mensagem genérica (e logar o detalhe no servidor), e reprovar:
o código original (devolve o traceback) e uma correção que só tira o traceback mas ainda devolve a
mensagem interna da exceção (str(exc)).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import ERROS_RAMOS, ErrosRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-041-erros-fintech", "lab-041-erros"),
    "sau": ("LAB-042-erros-saude", "lab-042-erros"),
    "ind": ("LAB-043-erros-industria", "lab-043-erros"),
}
SERVICO = "/workspace/services/erro_service.py"

VULN = (
    "import traceback\n\n\n"
    "class ErroService:\n"
    "    def resposta(self, exc: Exception) -> dict[str, str]:\n"
    '        """Monta o corpo JSON de erro para devolver ao cliente."""\n'
    "        # Expõe a mensagem interna e o traceback completo na resposta ao cliente.\n"
    '        return {"erro": str(exc), "detalhe": traceback.format_exc()}\n'
)
CORRETO = (
    "import logging\n\n"
    'logger = logging.getLogger("erro")\n\n\n'
    "class ErroService:\n"
    "    def resposta(self, exc: Exception) -> dict[str, str]:\n"
    '        """Monta o corpo JSON de erro para devolver ao cliente."""\n'
    "        # Registra o detalhe no servidor e devolve ao cliente só uma mensagem genérica.\n"
    '        logger.error("Falha ao processar a solicitação", exc_info=exc)\n'
    '        return {"erro": "Erro interno ao processar a solicitação."}\n'
)
# Tira o traceback, mas ainda devolve a mensagem interna da exceção (str(exc)).
SO_SEM_TRACEBACK = (
    "import traceback\n\n\n"
    "class ErroService:\n"
    "    def resposta(self, exc: Exception) -> dict[str, str]:\n"
    '        """Monta o corpo JSON de erro para devolver ao cliente."""\n'
    '        return {"erro": str(exc)}\n'
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
def test_original_code_leaks_traceback(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # Relatório válido funciona, mas o erro vaza o traceback (não traz mensagem genérica).
    assert r["relatorio-ok"], r
    assert not r["erro-sem-traceback"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_generic_error_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_dropping_traceback_only_still_leaks_exception_message(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_SEM_TRACEBACK)
    r = lab.evaluate(ev, ref)
    # Sem traceback, mas ainda devolve str(exc) (não é mensagem genérica): reprovado.
    assert not r["erro-sem-traceback"], r


@pytest.mark.parametrize("r", ERROS_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: ErrosRamo) -> None:
    expected = {
        f"erros-verbosos/answer/metodo-{r.ramo}-v1": "resposta",
        f"erros-verbosos/answer/aparece-{r.ramo}-v1": "aparece",
        f"erros-verbosos/answer/onde-{r.ramo}-v1": "log",
        f"erros-verbosos/answer/mensagem-{r.ramo}-v1": "genérica",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
