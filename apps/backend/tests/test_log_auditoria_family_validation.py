"""Suíte da família log-auditoria (LAB-077..079) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa registrar ``login_falhou`` em todo caminho de falha, sem a senha, e reprovar: o código
original (só registra o login certo), uma correção que só registra a senha errada (o login que não
existe continua sem rastro) e uma que grava a senha digitada na trilha.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import AUDITORIA_RAMOS, AuditoriaRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-077-log-auditoria-banco", "lab-077-log-auditoria"),
    "sau": ("LAB-078-log-auditoria-saude", "lab-078-log-auditoria"),
    "ind": ("LAB-079-log-auditoria-industria", "lab-079-log-auditoria"),
}
ARQUIVO = "/workspace/services/auth_service.py"
VULN = (
    "        if encontrado is None:\n"
    "            return None\n"
    "        conta, senha_hash = encontrado\n"
    "        if check_password_hash(senha_hash, senha):\n"
    '            self._auditoria.registrar("login_ok", login, ip)\n'
    "            return conta\n"
    "        return None\n"
)
CORRETO = (
    "        if encontrado is not None and check_password_hash(encontrado[1], senha):\n"
    '            self._auditoria.registrar("login_ok", login, ip)\n'
    "            return encontrado[0]\n"
    '        self._auditoria.registrar("login_falhou", login, ip)\n'
    "        return None\n"
)
SO_SENHA_ERRADA = VULN.rsplit("        return None\n", 1)[0] + (
    '        self._auditoria.registrar("login_falhou", login, ip)\n        return None\n'
)
COM_SENHA = CORRETO.replace('"login_falhou", login, ip', '"login_falhou", login + " " + senha, ip')


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
def test_original_does_not_record_failures(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, None)
    assert r["sucesso-registrado"], r
    assert not r["falha-registrada"], r
    assert not r["login-inexistente-registrado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_recording_every_failure_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, CORRETO)
    assert all(r.values()), r


def test_only_wrong_password_misses_unknown_login(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", SO_SENHA_ERRADA)
    assert r["falha-registrada"], r
    assert not r["login-inexistente-registrado"], r


def test_recording_the_password_fails(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", COM_SENHA)
    assert not r["sem-senha-na-trilha"], r


@pytest.mark.parametrize("r", AUDITORIA_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: AuditoriaRamo) -> None:
    expected = {
        f"log-auditoria/answer/evento-{r.ramo}-v1": "login_ok",
        f"log-auditoria/answer/falhas-{r.ramo}-v1": "0",
        f"log-auditoria/answer/segredo-{r.ramo}-v1": "senha",
        f"log-auditoria/answer/metodo-{r.ramo}-v1": "autenticar",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
