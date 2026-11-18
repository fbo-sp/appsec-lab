"""Suíte da família mob-app-adulterado (LAB-098..100) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção faz ``RecursoService.liberar`` ignorar o plano e a integridade que o app informa, conferir o
selo da loja simulada (``AtestacaoService.verificar``) e decidir o plano pelo cadastro. A suíte
reprova: o código original, a correção só pelo cadastro (sem selo), a correção só pelo selo (plano do
pedido) e a correção certa com o app ainda modificado (selo ``app_modificado``).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import ADULTERADO_RAMOS, AdulteradoRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-098-mob-app-adulterado-fintech", "lab-098-mobile"),
    "sau": ("LAB-099-mob-app-adulterado-saude", "lab-099-mobile"),
    "ind": ("LAB-100-mob-app-adulterado-industria", "lab-100-mobile"),
}
SERVICO = "/workspace/services/recurso_service.py"
REGRAS = "/workspace/static/regras.js"
VULN = (
    'plano = dados.get("plano")\n'
    '        app_integro = dados.get("integridade") == "ok"\n'
    '        return app_integro and plano == "avancado"'
)
SELO = 'if not self._atestacao.verificar(dados.get("selo"), conta_id):\n            return False\n        '
CADASTRO = 'return self._assinaturas.plano_da_conta(conta_id) == "avancado"'
CORRECAO = ((SERVICO, VULN, SELO + CADASTRO),)
SO_CADASTRO = ((SERVICO, VULN, CADASTRO),)
SO_SELO = ((SERVICO, VULN, SELO + 'return dados.get("plano") == "avancado"'),)
APP_MODIFICADO = ((REGRAS, "return conta.plano;", 'return "avancado";'),)


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
def test_original_trusts_what_the_app_says(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, ())
    assert r["avancado-com-selo-liberado"], r
    assert not r["basico-declarando-avancado-recusado"], r
    assert not r["selo-forjado-recusado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_seal_and_registry_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, CORRECAO)
    assert all(r.values()), r


def test_registry_without_seal_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", SO_CADASTRO)
    assert r["basico-declarando-avancado-recusado"], r
    assert not r["selo-forjado-recusado"], r


def test_seal_with_plan_from_request_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", SO_SELO)
    assert r["selo-forjado-recusado"], r
    assert not r["basico-declarando-avancado-recusado"], r


def test_modified_app_gets_refused_after_fix(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", CORRECAO + APP_MODIFICADO)
    assert not r["avancado-com-selo-liberado"], r


@pytest.mark.parametrize("r", ADULTERADO_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: AdulteradoRamo) -> None:
    expected = {
        f"mob-app-adulterado/answer/regras-{r.ramo}-v1": "regras.js",
        f"mob-app-adulterado/answer/liberou-{r.ramo}-v1": "sim",
        f"mob-app-adulterado/answer/veredito-{r.ramo}-v1": "app_modificado",
        f"mob-app-adulterado/answer/metodo-{r.ramo}-v1": "liberar",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
