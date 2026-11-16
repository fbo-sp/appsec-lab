"""Suíte da família Mass Assignment (LAB-008..010) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa aprovar listas de permissão (ignorando ou recusando campos extras) e reprovar o código
original e listas de bloqueio, que esquecem colunas como ``login``.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import MASSA_RAMOS, MassaRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-008-massa-fintech", "lab-008-massa", "pacote"),
    "sau": ("LAB-009-massa-saude", "lab-009-massa", "plano"),
    "ind": ("LAB-010-massa-energia", "lab-010-massa", "categoria"),
}
SERVICE = "/workspace/services/perfil_service.py"
VULNERABLE = "        self._repositorio.atualizar(usuario_id, dados)\n"
CLASSE = "class PerfilService:\n"
PROTEGIDOS = ("perfil-mantido", "area-restrita", "negocio-mantido", "login-mantido")


def _fixes(campo: str) -> dict[str, str]:
    return {
        "ignora-extras": (
            '        permitidos = {c: dados[c] for c in ("email", "telefone") if c in dados}\n'
            "        if not permitidos:\n"
            '            raise ValueError("Informe e-mail ou telefone.")\n'
            "        self._repositorio.atualizar(usuario_id, permitidos)\n"
        ),
        "recusa-extras": (
            '        extras = set(dados) - {"email", "telefone"}\n'
            "        if extras:\n"
            '            raise ValueError(f"Campos não permitidos: {sorted(extras)}")\n'
            "        self._repositorio.atualizar(usuario_id, dados)\n"
        ),
        # Erradas: listas de bloqueio.
        "bloqueia-perfil": '        dados.pop("perfil", None)\n' + VULNERABLE,
        "bloqueia-perfil-e-negocio": (
            f'        for proibido in ("perfil", "{campo}"):\n'
            "            dados.pop(proibido, None)\n" + VULNERABLE
        ),
    }


@pytest.fixture(scope="module")
def runtime() -> Iterator[tuple[Any, Any]]:
    docker_lab_image()  # pula sem DOCKER_CONTRACT_TESTS=1 antes de tocar no Docker
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    try:
        yield rt, DockerEvaluator()
    finally:
        for owned in rt.list_owned():
            rt.terminate(owned.runtime_ref)


def _lab(ramo: str) -> tuple[LabUnderTest, str]:
    lab_dir, name, campo = LABS[ramo]
    return LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local")), campo


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_code_lets_the_user_change_protected_fields(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab, _ = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert r["contato-editavel"] and r["contato-salvo"], r
    assert not any(r[k] for k in PROTEGIDOS), r


@pytest.mark.parametrize("ramo", sorted(LABS))
@pytest.mark.parametrize("fix", ["ignora-extras", "recusa-extras"])
def test_allowlists_pass_every_check(runtime: tuple[Any, Any], ramo: str, fix: str) -> None:
    rt, ev = runtime
    lab, campo = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICE, VULNERABLE, _fixes(campo)[fix])
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_documented_fix_passes_every_check(runtime: tuple[Any, Any]) -> None:
    """A correção escrita na etapa 5 (método inteiro + CAMPOS_EDITAVEIS acima da classe)."""
    rt, ev = runtime
    lab, _ = _lab("sau")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICE, CLASSE, 'CAMPOS_EDITAVEIS = ("email", "telefone")\n\n\n' + CLASSE)
    replace_in_file(
        box,
        SERVICE,
        "        if not isinstance(dados, dict) or not dados:\n"
        '            raise ValueError("Envie em JSON os campos que quer atualizar.")\n'
        "        self._validar_contato(dados)\n"
        + VULNERABLE
        + '        logger.info("Perfil atualizado: usuario=%s campos=%s", usuario_id, sorted(dados))\n',
        "        if not isinstance(dados, dict):\n"
        '            raise ValueError("Envie em JSON os campos que quer atualizar.")\n'
        "        permitidos = {campo: dados[campo] for campo in CAMPOS_EDITAVEIS if campo in dados}\n"
        "        if not permitidos:\n"
        '            raise ValueError("Informe e-mail ou telefone.")\n'
        "        self._validar_contato(permitidos)\n"
        "        self._repositorio.atualizar(usuario_id, permitidos)\n"
        '        logger.info("Perfil atualizado: usuario=%s campos=%s", usuario_id, sorted(permitidos))\n',
    )
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


@pytest.mark.parametrize(
    ("fix", "falham"),
    [
        ("bloqueia-perfil", ("negocio-mantido", "login-mantido")),
        ("bloqueia-perfil-e-negocio", ("login-mantido",)),
    ],
)
def test_blocklists_are_rejected(runtime: tuple[Any, Any], fix: str, falham: tuple[str, ...]) -> None:
    rt, ev = runtime
    lab, campo = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICE, VULNERABLE, _fixes(campo)[fix])
    r = lab.evaluate(ev, ref)
    assert r["perfil-mantido"] and r["area-restrita"], r
    assert not any(r[k] for k in falham), r


@pytest.mark.parametrize("r", MASSA_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: MassaRamo) -> None:
    expected = {
        f"mass-assignment/answer/role-{r.ramo}-v1": r.perfil_comum,
        f"mass-assignment/answer/business-value-{r.ramo}-v1": r.valor_ataque,
        f"mass-assignment/answer/business-benefit-{r.ramo}-v1": r.beneficio[0],
        f"mass-assignment/answer/privileged-key-{r.ramo}-v1": r.chave_priv,
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
