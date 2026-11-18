"""Suíte da família mob-deep-link (LAB-089..091) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção faz o caminho do deep link criar a operação pendente, com código de confirmação de uso
único, e a suíte reprova o código original (o link executa a operação na hora).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import DEEPLINK_RAMOS, DeepLinkRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-089-mob-deep-link-fintech", "lab-089-mobile"),
    "sau": ("LAB-090-mob-deep-link-saude", "lab-090-mobile"),
    "ind": ("LAB-091-mob-deep-link-industria", "lab-091-mobile"),
}
ARQUIVO = "/workspace/services/operacao_service.py"
VULN = (
    '        """Operação vinda de um link do app (deep link): o atalho "um toque" da campanha."""\n'
    "        self._validar(alvo, detalhe)\n"
    '        operacao_id = self._operacoes.criar(conta_id, alvo, detalhe, "concluida", None, time.time())\n'
    '        return {"id": operacao_id, "status": "concluida", "alvo": alvo, "detalhe": detalhe}\n'
)
CORRETO = (
    '        """Operação vinda de um link (deep link): nunca executa direto, só cria a pendente para o usuário'
    ' confirmar."""\n'
    "        return self.iniciar(conta_id, alvo, detalhe)\n"
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


def _avaliar(rt: Any, ev: Any, ramo: str, novo: str | None) -> dict[str, bool]:
    lab_dir, name = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    box, ref = lab.provision(rt)
    try:
        if novo is not None:
            replace_in_file(box, ARQUIVO, VULN, novo)
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_link_executes_without_confirmation(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, None)
    assert r["botao-continua"], r
    assert not r["link-fica-pendente"], r
    assert not r["nada-executado-sem-confirmar"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_link_requires_single_use_confirmation(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, CORRETO)
    assert all(r.values()), r


@pytest.mark.parametrize("r", DEEPLINK_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: DeepLinkRamo) -> None:
    expected = {
        f"mob-deep-link/answer/metodo-confirma-{r.ramo}-v1": "confirmar",
        f"mob-deep-link/answer/status-{r.ramo}-v1": "concluida",
        f"mob-deep-link/answer/quem-{r.ramo}-v1": "qualquer pessoa",
        f"mob-deep-link/answer/metodo-{r.ramo}-v1": "iniciar_por_link",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
