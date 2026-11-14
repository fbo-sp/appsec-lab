"""Suíte do LAB-004 (Command Injection) contra Docker real (VAL-01/02). Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa aprovar soluções corretas (sem shell, validação por lista de permissão, ou ambas) e
reprovar a original e listas de bloqueio incompletas (ADR-010).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer

from tests.docker_support import lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LAB_DIR = "LAB-004-cmdi-industria"
SERVICE = "/workspace/services/diagnostico_service.py"
VULNERABLE = (
    '        comando = f"diag-clp {endereco}"\n'
    "        return self._executor.executar(comando, usar_shell=True)\n"
)
IMPORT = "from infra.executor_comandos import ExecutorComandos\n"
FIXES = {
    "documentada": (
        "        try:\n"
        "            ipaddress.IPv4Address(endereco)\n"
        "        except ValueError:\n"
        '            return "Endereço inválido. Informe um IPv4, por exemplo 10.20.1.15."\n'
        '        return self._executor.executar(["diag-clp", endereco], usar_shell=False)\n'
    ),
    "so-sem-shell": '        return self._executor.executar(["diag-clp", endereco], usar_shell=False)\n',
    "shlex-quote": (
        "        import shlex\n"
        '        return self._executor.executar(f"diag-clp {shlex.quote(endereco)}", usar_shell=True)\n'
    ),
    # Erradas: listas de bloqueio.
    "bloqueia-ponto-e-virgula": (
        '        endereco = endereco.replace(";", "")\n'
        '        comando = f"diag-clp {endereco}"\n'
        "        return self._executor.executar(comando, usar_shell=True)\n"
    ),
    "bloqueia-varios-menos-quebra": (
        '        for proibido in (";", "&", "|", "$", "`"):\n'
        '            endereco = endereco.replace(proibido, "")\n'
        '        comando = f"diag-clp {endereco}"\n'
        "        return self._executor.executar(comando, usar_shell=True)\n"
    ),
}
INJECTIONS = ("ponto-e-virgula", "e-comercial", "pipe", "ou-logico", "subshell", "crase", "quebra-de-linha")


@pytest.fixture(scope="module")
def env() -> Iterator[tuple[Any, Any, LabUnderTest]]:
    lab = LabUnderTest(LAB_DIR, lab_image(LAB_DIR, "cecyber-labs/lab-004-cmdi:local"))
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    try:
        yield rt, DockerEvaluator(), lab
    finally:
        for owned in rt.list_owned():
            rt.terminate(owned.runtime_ref)


def test_original_code_executes_injected_commands(env: tuple[Any, Any, LabUnderTest]) -> None:
    rt, ev, lab = env
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert r["clp-responde"] and r["clp-sem-resposta"], r
    assert not any(r[k] for k in INJECTIONS), r


@pytest.mark.parametrize("fix", ["documentada", "so-sem-shell", "shlex-quote"])
def test_correct_fixes_pass_every_check(env: tuple[Any, Any, LabUnderTest], fix: str) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    if fix == "documentada":
        replace_in_file(box, SERVICE, IMPORT, "import ipaddress\n\n" + IMPORT)
    replace_in_file(box, SERVICE, VULNERABLE, FIXES[fix])
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


@pytest.mark.parametrize(
    ("fix", "failing"),
    [
        ("bloqueia-ponto-e-virgula", ("e-comercial", "pipe", "subshell", "quebra-de-linha")),
        ("bloqueia-varios-menos-quebra", ("quebra-de-linha",)),
    ],
)
def test_blocklists_are_rejected(
    env: tuple[Any, Any, LabUnderTest], fix: str, failing: tuple[str, ...]
) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICE, VULNERABLE, FIXES[fix])
    r = lab.evaluate(ev, ref)
    assert not any(r[k] for k in failing), r


def test_forgetting_the_import_reports_the_error(env: tuple[Any, Any, LabUnderTest]) -> None:
    """Sem ``import ipaddress`` o módulo carrega, mas o teste falha com NameError (500), não com aprovação."""
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICE, VULNERABLE, FIXES["documentada"])
    r = lab.evaluate(ev, ref)
    assert not r["clp-responde"], r


def test_answer_suites_accept_documented_answers() -> None:
    expected = {
        "cmdi/answer/locate-program-v1": "diag-clp",
        "cmdi/answer/process-user-v1": "lab",
        "cmdi/answer/scada-file-v1": "scada.conf",
        "cmdi/answer/scada-password-v1": "SCADA-OPR-4471-KX",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
