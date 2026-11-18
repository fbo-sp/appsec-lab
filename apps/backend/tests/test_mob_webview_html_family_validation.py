"""Suíte da família mob-webview-html (LAB-092..094) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção tira o ``|safe`` do texto da mensagem e declara uma CSP restrita na página do WebView, e a
suíte reprova: o código original, um filtro que só remove ``<script`` (a carga nem usa script) e a
correção sem CSP.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import WEBVIEW_RAMOS, WebviewRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-092-mob-webview-html-fintech", "lab-092-mobile"),
    "sau": ("LAB-093-mob-webview-html-saude", "lab-093-mobile"),
    "ind": ("LAB-094-mob-webview-html-industria", "lab-094-mobile"),
}
ARQUIVO = "/workspace/templates/webview_mensagens.html"
TEXTO = "{{ m.texto|safe }}"
CSP = (
    "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'\">\n"
    "  <style>"
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


def _avaliar(rt: Any, ev: Any, ramo: str, trocas: tuple[tuple[str, str], ...]) -> dict[str, bool]:
    lab_dir, name = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    box, ref = lab.provision(rt)
    try:
        for old, new in trocas:
            replace_in_file(box, ARQUIVO, old, new)
        return lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_renders_message_as_html(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, ())
    assert r["mensagem-enviada"], r
    assert not r["sem-html-da-mensagem"], r
    assert not r["politica-de-conteudo"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_output_encoding_and_csp_pass(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, ((TEXTO, "{{ m.texto }}"), ("<style>", CSP)))
    assert all(r.values()), r


def test_removing_script_word_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", ((TEXTO, "{{ m.texto|replace('<script', '')|safe }}"),))
    assert not r["sem-html-da-mensagem"], r


def test_encoding_without_csp_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", ((TEXTO, "{{ m.texto }}"),))
    assert r["sem-html-da-mensagem"], r
    assert not r["politica-de-conteudo"], r


@pytest.mark.parametrize("r", WEBVIEW_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: WebviewRamo) -> None:
    expected = {
        f"mob-webview-html/answer/pagina-{r.ramo}-v1": "webview_mensagens.html",
        f"mob-webview-html/answer/aparencia-{r.ramo}-v1": "quadro",
        f"mob-webview-html/answer/filtro-{r.ramo}-v1": "safe",
        f"mob-webview-html/answer/csp-{r.ramo}-v1": "CSP",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
