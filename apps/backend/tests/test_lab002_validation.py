"""Suíte do LAB-002 (IDOR) contra Docker real (VAL-01/02). Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A verificação de dono precisa aprovar correções corretas e reprovar a original e "correções" que
protegem só a página, confiam em parâmetro da URL ou bloqueiam o próprio dono (ADR-010/ADR-015).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer

from tests.docker_support import lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LAB_DIR = "LAB-002-idor-banco"
SERVICE = "/workspace/services/comprovante_service.py"
CONTROLLER = "/workspace/controllers/comprovantes_controller.py"
REPOSITORY = "/workspace/repositories/comprovante_repository.py"
VULNERABLE = "        return self._repositorio.buscar_por_id(comprovante_id)\n"
FIXES = {
    "verifica-dono": (
        "        comprovante = self._repositorio.buscar_por_id(comprovante_id)\n"
        "        if comprovante is None or comprovante.cliente_id != cliente_id:\n"
        "            return None\n"
        "        return comprovante\n"
    ),
    # Filtra na consulta: o dado de outro cliente nem sai do banco.
    "filtra-na-consulta": (
        "        comprovante = self._repositorio.buscar_por_id(comprovante_id)\n"
        "        return comprovante if comprovante and comprovante.cliente_id == cliente_id else None\n"
    ),
    # Errada: bloqueia tudo (o próprio dono deixa de ver).
    "bloqueia-tudo": "        return None\n",
}
# Errada: protege só a página HTML; a API continua aberta.
HTML_ONLY = (
    "    if comprovante is None:\n        abort(404)\n",
    '    if comprovante is None or comprovante.cliente_id != session["cliente_id"]:\n        abort(404)\n',
)
# Errada: confia no cliente_id da URL quando informado.
TRUSTS_PARAM = (
    '        comprovante = _servico(conexao).obter(comprovante_id, session["cliente_id"])\n'
    '    if comprovante is None:\n        return {"erro": "comprovante não encontrado"}, 404\n',
    '        comprovante = _servico(conexao).obter(comprovante_id, session["cliente_id"])\n'
    '    dono = int(request.args.get("cliente_id", session["cliente_id"]))\n'
    "    if comprovante is None or comprovante.cliente_id != dono:\n"
    '        return {"erro": "comprovante não encontrado"}, 404\n',
)


@pytest.fixture(scope="module")
def env() -> Iterator[tuple[Any, Any, LabUnderTest]]:
    lab = LabUnderTest(LAB_DIR, lab_image(LAB_DIR, "cecyber-labs/lab-002-idor:local"))
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    try:
        yield rt, DockerEvaluator(), lab
    finally:
        for owned in rt.list_owned():
            rt.terminate(owned.runtime_ref)


def test_original_code_leaks_other_customers(env: tuple[Any, Any, LabUnderTest]) -> None:
    rt, ev, lab = env
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert r["proprio-comprovante"] and r["propria-api"] and r["lista-propria"], r
    assert r["dono-ve-o-seu"] and r["sem-login"], r
    assert not r["outro-cliente-pagina"] and not r["outro-cliente-api"] and not r["parametro-forjado"], r


@pytest.mark.parametrize("fix", ["verifica-dono", "filtra-na-consulta"])
def test_correct_fixes_pass_every_check(env: tuple[Any, Any, LabUnderTest], fix: str) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICE, VULNERABLE, FIXES[fix])
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_blocking_everyone_is_rejected(env: tuple[Any, Any, LabUnderTest]) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICE, VULNERABLE, FIXES["bloqueia-tudo"])
    r = lab.evaluate(ev, ref)
    assert not r["proprio-comprovante"] and not r["dono-ve-o-seu"], r


def test_protecting_only_the_html_page_is_rejected(env: tuple[Any, Any, LabUnderTest]) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, CONTROLLER, *HTML_ONLY)
    r = lab.evaluate(ev, ref)
    assert r["outro-cliente-pagina"] and not r["outro-cliente-api"], r


def test_trusting_a_url_parameter_is_rejected(env: tuple[Any, Any, LabUnderTest]) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(
        box,
        CONTROLLER,
        "from flask import Blueprint, abort, current_app, render_template, session\n",
        "from flask import Blueprint, abort, current_app, render_template, request, session\n",
    )
    replace_in_file(box, CONTROLLER, *TRUSTS_PARAM)
    r = lab.evaluate(ev, ref)
    assert r["outro-cliente-api"] and not r["parametro-forjado"], r


def test_answer_suites_accept_documented_answers() -> None:
    expected = {
        "idor/answer/locate-lookup-v1": "ComprovanteRepository.buscar_por_id",
        "idor/answer/latest-receipt-v1": "10458",
        "idor/answer/other-payer-v1": "Rodrigo Tavares Lima",
        "idor/answer/leaked-count-v1": "34",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
