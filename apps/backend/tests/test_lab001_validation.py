"""Suíte do LAB-001 contra Docker real (VAL-01/02). Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A suíte comportamental da correção precisa aprovar soluções corretas e reprovar a original e
"correções" incorretas, sempre avaliando uma cópia isolada do workspace (ADR-010).
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import pytest
import yaml
from app.runtime.port import ProvisionRequest, ResourceLimits, RuntimePhase
from app.validation.port import EvaluationRequest
from app.validation.suites import AnswerSuite, HttpSuite, get_suite, normalize_answer

from tests.docker_support import LABS, lab001_image

SUITE_REF = "sqli/python-flask/parameterized-search-v1"
# Mesmo comando do manifesto: a saída do processo também vai para /tmp/app.log.
CMD = tuple(
    yaml.safe_load((LABS / "LAB-001-sqli-clinica" / "manifest.yaml").read_text(encoding="utf-8"))["variants"][
        0
    ]["startup"]["command"]
)
REPO = "/workspace/repositories/medico_repository.py"
VULNERABLE = (
    "        sql = f\"SELECT id, nome, especialidade, crm FROM medicos WHERE nome LIKE '%{termo}%'\"\n"
    "        linhas = self._conexao.execute(sql).fetchall()\n"
)
FIXES = {
    "parametrizada": (
        '        sql = "SELECT id, nome, especialidade, crm FROM medicos WHERE nome LIKE ?"\n'
        '        linhas = self._conexao.execute(sql, (f"%{termo}%",)).fetchall()\n'
    ),
    "parametro-nomeado": (
        '        sql = "SELECT id, nome, especialidade, crm FROM medicos WHERE nome LIKE :termo"\n'
        '        linhas = self._conexao.execute(sql, {"termo": f"%{termo}%"}).fetchall()\n'
    ),
    "remove-aspas": (
        '        termo = termo.replace("\'", "")\n'
        "        sql = f\"SELECT id, nome, especialidade, crm FROM medicos WHERE nome LIKE '%{termo}%'\"\n"
        "        linhas = self._conexao.execute(sql).fetchall()\n"
    ),
    # Colagem sem recuo (caso real de teste do PO): a 2ª linha cai na coluna 0 e o método termina antes.
    "recuo-quebrado": (
        '        sql = "SELECT id, nome, especialidade, crm FROM medicos WHERE nome LIKE ?"\n'
        'linhas = self._conexao.execute(sql, (f"%{termo}%",)).fetchall()\n'
    ),
    "bloqueia-aspas": (
        '        if "\'" in termo:\n'
        "            raise ValueError('caractere proibido')\n"
        "        sql = f\"SELECT id, nome, especialidade, crm FROM medicos WHERE nome LIKE '%{termo}%'\"\n"
        "        linhas = self._conexao.execute(sql).fetchall()\n"
    ),
}


@pytest.fixture(scope="module")
def env() -> Iterator[tuple[Any, Any, str]]:
    image = lab001_image()
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    try:
        yield rt, DockerEvaluator(), image
    finally:
        for owned in rt.list_owned():
            rt.terminate(owned.runtime_ref)


def _provision(rt: Any, image: str) -> tuple[Any, str]:
    ref = rt.provision(
        ProvisionRequest(
            session_id=str(uuid.uuid4()),
            lab_release="LAB-001@1.0.1",
            variant_id="python-flask",
            image_digest=image,
            runtime_profile="web-basic",
            resources=ResourceLimits(500, 512, 256, 64),
            egress_profile="deny-all",
            exposed_port=8080,
            expires_at=datetime(2030, 1, 1, tzinfo=UTC),
            startup_command=CMD,
            workspace_path="/workspace",
        )
    )
    deadline = time.monotonic() + 90
    while rt.inspect(ref).phase is RuntimePhase.PENDING and time.monotonic() < deadline:
        time.sleep(0.5)
    assert rt.inspect(ref).phase is RuntimePhase.READY
    return rt._client.containers.get(ref), ref


def _evaluate(ev: Any, ref: str, image: str) -> dict[str, bool]:
    out = _outcome(ev, ref, image)
    assert out.app_started, out.app_log_tail
    results: dict[str, bool] = out.results
    return results


def _outcome(ev: Any, ref: str, image: str) -> Any:
    suite = get_suite(SUITE_REF)
    assert isinstance(suite, HttpSuite)
    req = EvaluationRequest(
        submission_id=str(uuid.uuid4()),
        runtime_ref=ref,
        image_digest=image,
        workspace_path="/workspace",
        startup_command=CMD,
        app_port=8080,
        checks=[
            {
                "id": c.id,
                "path": c.path,
                "method": c.method,
                "form": c.form,
                "expect_status": c.expect_status,
                "contains": list(c.contains),
                "not_contains": list(c.not_contains),
            }
            for c in suite.checks
        ],
        cpu_millicores=500,
        memory_mib=512,
        pids_max=64,
        timeout_seconds=90,
    )
    out = ev.evaluate(req)
    assert out.error is None, out.error
    return out


def _apply(box: Any, replacement: str) -> None:
    code = (
        "import pathlib,sys; p=pathlib.Path(sys.argv[1]); s=p.read_text(encoding='utf-8');"
        "assert sys.argv[2] in s; p.write_text(s.replace(sys.argv[2], sys.argv[3]), encoding='utf-8')"
    )
    res = box.exec_run(["python", "-c", code, REPO, VULNERABLE, replacement], user="10001")
    assert res.exit_code == 0, res.output


def test_original_vulnerable_code_fails_security_checks(env: tuple[Any, Any, str]) -> None:
    rt, ev, image = env
    _, ref = _provision(rt, image)
    r = _evaluate(ev, ref, image)
    assert r["busca-parcial"] and r["busca-vazia"]
    assert not any(r[k] for k in ("apostrofo", "aspa-sem-erro", "union-pacientes", "union-configuracoes"))
    assert not r["condicao-injetada"]


@pytest.mark.parametrize("fix", ["parametrizada", "parametro-nomeado"])
def test_correct_fixes_pass_every_check(env: tuple[Any, Any, str], fix: str) -> None:
    rt, ev, image = env
    box, ref = _provision(rt, image)
    _apply(box, FIXES[fix])
    r = _evaluate(ev, ref, image)
    assert all(r.values()), r


@pytest.mark.parametrize(("fix", "failing"), [("remove-aspas", "apostrofo"), ("bloqueia-aspas", "apostrofo")])
def test_incorrect_fixes_are_rejected(env: tuple[Any, Any, str], fix: str, failing: str) -> None:
    rt, ev, image = env
    box, ref = _provision(rt, image)
    _apply(box, FIXES[fix])
    r = _evaluate(ev, ref, image)
    assert not r[failing] and not all(r.values()), r


def test_answer_suites_accept_documented_answers() -> None:
    expected = {
        "sqli/answer/locate-query-v1": "MedicoRepository.buscar_por_nome",
        "sqli/answer/error-type-v1": "OperationalError",
        "sqli/answer/column-count-v1": "4",
        "sqli/answer/integration-token-v1": "VP-INT-7Q2K-93XD",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}


def test_code_that_does_not_start_reports_the_error(env: tuple[Any, Any, str]) -> None:
    """Recuo quebrado: em vez de 7 falhas de segurança, a avaliação diz que a aplicação não subiu e por quê.

    O mesmo erro também vai para /tmp/app.log da sessão, que o aluno lê pelo terminal.
    """
    rt, ev, image = env
    box, ref = _provision(rt, image)
    _apply(box, FIXES["recuo-quebrado"])
    out = _outcome(ev, ref, image)
    assert not out.app_started and not out.results
    assert "IndentationError" in (out.app_log_tail or "")
    deadline = time.monotonic() + 15
    log = ""
    while "IndentationError" not in log and time.monotonic() < deadline:
        time.sleep(1)
        log = box.exec_run(["tail", "-n", "30", "/tmp/app.log"]).output.decode()
    assert "IndentationError" in log
