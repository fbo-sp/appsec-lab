"""Suíte da família CSRF (LAB-011..013) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa aprovar o token sincronizador por sessão e reprovar o código original, um token fixo
no código, um token gerado mas não conferido e uma checagem de Fetch Metadata que aceita pedido sem o
cabeçalho.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import CSRF_RAMOS, CsrfRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-011-csrf-seguros", "lab-011-csrf", "indenizacao"),
    "sau": ("LAB-012-csrf-hospital", "lab-012-csrf", "laudos"),
    "ind": ("LAB-013-csrf-energia", "lab-013-csrf", "alarmes"),
}
IMPORT = (
    "from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for\n"
)
NEW_IMPORT = (
    "import secrets\n\n"
    "from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, "
    "url_for\n"
)
COMENTARIO = "    # O usuário já está logado (cookie de sessão), então a alteração é aceita.\n"
CONFERE = (
    '    esperado = session.get("csrf_token")\n'
    '    enviado = request.form.get("csrf_token", "")\n'
    "    if not esperado or not secrets.compare_digest(enviado, esperado):\n"
    "        abort(400)\n"
)
TOKEN_FN = (
    "def _token_csrf() -> str:\n"
    '    if "csrf_token" not in session:\n'
    '        session["csrf_token"] = secrets.token_urlsafe(32)\n'
    '    return session["csrf_token"]\n\n\n'
)
PROTEGIDOS = (
    "sem-token-recusado",
    "sem-token-nao-gravou",
    "token-de-outra-sessao-recusado",
    "outra-sessao-nao-gravou",
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


def _lab(ramo: str) -> tuple[LabUnderTest, str, str, str]:
    lab_dir, name, modulo = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    controller = f"/workspace/controllers/{modulo}_controller.py"
    template = f"/workspace/templates/{modulo}.html"
    return lab, controller, template, modulo


def _hidden(template_value: str) -> str:
    return f'  <input type="hidden" name="csrf_token" value="{template_value}">\n'


def _form_line(box: Any, template: str) -> str:
    out = box.exec_run(["grep", "-m1", '<form method="post"', template]).output.decode()
    assert out, "form não encontrado"
    return out


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_code_accepts_forged_posts(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab, *_ = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert not r["formulario-com-token"], r
    assert not r["sem-token-recusado"] and not r["sem-token-nao-gravou"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_documented_synchronizer_token_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab, controller, template, modulo = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, controller, IMPORT, NEW_IMPORT)
    replace_in_file(box, controller, f"@{modulo}_bp.get(", TOKEN_FN + f"@{modulo}_bp.get(")
    replace_in_file(box, controller, "historico=historico)", "historico=historico, csrf_token=_token_csrf())")
    replace_in_file(box, controller, COMENTARIO, CONFERE)
    form = _form_line(box, template)
    replace_in_file(box, template, form, form + _hidden("{{ csrf_token }}"))
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_fixed_token_is_rejected(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab, controller, template, _ = _lab("sau")
    box, ref = lab.provision(rt)
    replace_in_file(
        box,
        controller,
        COMENTARIO,
        '    if request.form.get("csrf_token") != "token-fixo-2026":\n'
        '        return "Pedido inválido", 400\n',
    )
    form = _form_line(box, template)
    replace_in_file(box, template, form, form + _hidden("token-fixo-2026"))
    r = lab.evaluate(ev, ref)
    assert r["sem-token-recusado"] and r["alteracao-legitima"], r
    assert not r["token-de-outra-sessao-recusado"] and not r["outra-sessao-nao-gravou"], r


def test_token_generated_but_not_checked_is_rejected(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab, controller, template, modulo = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, controller, IMPORT, NEW_IMPORT)
    replace_in_file(box, controller, f"@{modulo}_bp.get(", TOKEN_FN + f"@{modulo}_bp.get(")
    replace_in_file(box, controller, "historico=historico)", "historico=historico, csrf_token=_token_csrf())")
    form = _form_line(box, template)
    replace_in_file(box, template, form, form + _hidden("{{ csrf_token }}"))
    r = lab.evaluate(ev, ref)
    assert r["formulario-com-token"] and r["alteracao-legitima"], r
    assert not any(r[k] for k in PROTEGIDOS), r


def test_permissive_fetch_metadata_check_is_rejected(runtime: tuple[Any, Any]) -> None:
    """Recusa ``same-site``/``cross-site``, mas aceita pedido sem o cabeçalho (clientes antigos, scripts)."""
    rt, ev = runtime
    lab, controller, _, _ = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(
        box,
        controller,
        COMENTARIO,
        '    if request.headers.get("Sec-Fetch-Site", "same-origin") != "same-origin":\n'
        '        return "Origem não permitida", 403\n',
    )
    r = lab.evaluate(ev, ref)
    assert not r["sem-token-recusado"] and not r["sem-token-nao-gravou"], r


@pytest.mark.parametrize("r", CSRF_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: CsrfRamo) -> None:
    expected = {
        f"csrf/answer/field-name-{r.ramo}-v1": r.campo,
        f"csrf/answer/samesite-{r.ramo}-v1": "Lax",
        f"csrf/answer/forged-value-{r.ramo}-v1": r.valor_ataque,
        f"csrf/answer/fetch-site-{r.ramo}-v1": "same-site",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
