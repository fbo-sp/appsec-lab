"""Suíte da família autorizacao-api (LAB-038..040) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa exigir o papel admin para a API administrativa, e reprovar: o código original
(libera para qualquer autenticado) e uma correção que só confere se o papel é "não vazio" (o usuário
comum, que tem papel "comum", continua passando).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import AUTORIZACAO_RAMOS, AutorizacaoRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-038-autorizacao-banco", "lab-038-autorizacao"),
    "sau": ("LAB-039-autorizacao-saude", "lab-039-autorizacao"),
    "ind": ("LAB-040-autorizacao-industria", "lab-040-autorizacao"),
}
SERVICO = "/workspace/services/permissao_service.py"

VULN = (
    "    def pode_administrar(self, papel: str) -> bool:\n"
    '        """Diz se o papel pode usar as funções administrativas."""\n'
    "        # Não confere o papel: qualquer usuário autenticado é liberado.\n"
    "        return True\n"
)
CORRETO = (
    "    def pode_administrar(self, papel: str) -> bool:\n"
    '        """Diz se o papel pode usar as funções administrativas."""\n'
    '        return papel == "admin"\n'
)
# Só confere se o papel é "não vazio": o usuário comum (papel "comum") continua passando.
SO_TRUTHY = (
    "    def pode_administrar(self, papel: str) -> bool:\n"
    '        """Diz se o papel pode usar as funções administrativas."""\n'
    "        return bool(papel)\n"
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
def test_original_code_allows_common_user(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # Admin usa a API; mas o usuário comum NÃO é barrado (a API responde 200, não 403).
    assert r["admin-liberado"], r
    assert not r["comum-bloqueado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_role_check_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_truthy_check_still_allows_common_user(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_TRUTHY)
    r = lab.evaluate(ev, ref)
    # Papel "comum" é não vazio, então continua passando: reprovado.
    assert r["admin-liberado"], r
    assert not r["comum-bloqueado"], r


@pytest.mark.parametrize("r", AUTORIZACAO_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: AutorizacaoRamo) -> None:
    expected = {
        f"autorizacao-api/answer/metodo-{r.ramo}-v1": "pode_administrar",
        f"autorizacao-api/answer/resultado-{r.ramo}-v1": "conseguiu",
        f"autorizacao-api/answer/conceito-{r.ramo}-v1": "autorização",
        f"autorizacao-api/answer/papel-{r.ramo}-v1": "admin",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
