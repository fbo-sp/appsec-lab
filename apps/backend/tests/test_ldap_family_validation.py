"""Suíte da família ldap-injection (LAB-044..046) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa escapar os caracteres especiais do filtro LDAP antes de montá-lo, e reprovar:
o código original (junta o nome cru no filtro, então ``*`` vira curinga e lista o diretório inteiro)
e uma correção incompleta que escapa só os parênteses e esquece o ``*`` (o curinga continua vazando).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import LDAP_RAMOS, LdapRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-044-ldap-fintech", "lab-044-diretorio"),
    "sau": ("LAB-045-ldap-saude", "lab-045-diretorio"),
    "ind": ("LAB-046-ldap-industria", "lab-046-diretorio"),
}
SERVICO = "/workspace/services/busca_service.py"

VULN = (
    "        # Junta o nome cru no filtro: um * digitado vira curinga e lista tudo.\n"
    '        filtro = f"(cn={nome})"\n'
    "        return buscar(filtro)\n"
)
CORRETO = (
    "        # Escapa os caracteres especiais do filtro LDAP: a entrada vira texto, não sintaxe.\n"
    "        nome_seguro = nome\n"
    '        for especial, escapado in (("\\\\", r"\\5c"), ("*", r"\\2a"), ("(", r"\\28"), (")", r"\\29")):\n'
    "            nome_seguro = nome_seguro.replace(especial, escapado)\n"
    '        filtro = f"(cn={nome_seguro})"\n'
    "        return buscar(filtro)\n"
)
# Escapa só os parênteses e esquece o *: o curinga continua vazando o diretório inteiro.
SO_PARENTESES = (
    '        nome_seguro = nome.replace("(", r"\\28").replace(")", r"\\29")\n'
    '        filtro = f"(cn={nome_seguro})"\n'
    "        return buscar(filtro)\n"
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
def test_original_code_leaks_whole_directory(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # A busca legítima funciona, mas buscar por * vaza o diretório inteiro: reprovado.
    assert r["busca-legitima"], r
    assert not r["curinga-nao-vaza-tudo"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_full_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_escaping_only_parens_still_leaks(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_PARENTESES)
    r = lab.evaluate(ev, ref)
    # A busca legítima segue funcionando, mas o * não foi escapado e continua vazando tudo: reprovado.
    assert r["busca-legitima"], r
    assert not r["curinga-nao-vaza-tudo"], r


@pytest.mark.parametrize("r", LDAP_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: LdapRamo) -> None:
    expected = {
        f"ldap-injection/answer/metodo-{r.ramo}-v1": "por_nome",
        f"ldap-injection/answer/comportamento-{r.ramo}-v1": "o diretório inteiro",
        f"ldap-injection/answer/defesa-{r.ramo}-v1": "escapar",
        f"ldap-injection/answer/onde-{r.ramo}-v1": "texto",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
