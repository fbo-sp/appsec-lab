"""Suíte da família XSS (LAB-005..007) contra Docker real (VAL-01/02). Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa aprovar soluções corretas (tirar ``|safe`` ou trocar por ``|e`` nos dois templates) e
reprovar o código original, a correção feita só na busca e listas de bloqueio no ``limpar_texto``.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import XSS_RAMOS, XssRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-005-xss-banco", "lab-005-xss", "favorecidos", "favorecido"),
    "sau": ("LAB-006-xss-saude", "lab-006-xss", "exames", "exame"),
    "ind": ("LAB-007-xss-energia", "lab-007-xss", "ordens", "ordem"),
}
BUSCA_SAFE = "{{ termo|safe }}"
PAINEL_SAFE = "{{ item.nota|safe }}"
BLOQUEIO_ORIGINAL = '_TAG_SCRIPT = re.compile(r"</?script[^>]*>", re.IGNORECASE)'
BUSCA = ("busca-img-onerror", "busca-svg-onload", "busca-details-ontoggle")
PAINEL = ("painel-codificado",)


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


def _lab(ramo: str) -> tuple[LabUnderTest, str, str]:
    lab_dir, name, listagem, entidade = LABS[ramo]
    lab = LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))
    return lab, f"/workspace/templates/{listagem}.html", f"/workspace/services/{entidade}_service.py"


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_code_is_vulnerable_in_search_and_panel(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab, _, _ = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert r["busca-legitima"] and r["cadastro-funciona"] and r["painel-continua"], r
    assert r["painel-restrito"], r
    assert not any(r[k] for k in BUSCA + PAINEL), r


@pytest.mark.parametrize("ramo", sorted(LABS))
@pytest.mark.parametrize("filtro", ["", "|e"])
def test_encoding_fix_passes_every_check(runtime: tuple[Any, Any], ramo: str, filtro: str) -> None:
    rt, ev = runtime
    lab, listagem, _ = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, listagem, BUSCA_SAFE, "{{ termo" + filtro + " }}")
    replace_in_file(box, "/workspace/templates/painel.html", PAINEL_SAFE, "{{ item.nota" + filtro + " }}")
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_fixing_only_the_search_is_rejected(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab, listagem, _ = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, listagem, BUSCA_SAFE, "{{ termo }}")
    r = lab.evaluate(ev, ref)
    assert all(r[k] for k in BUSCA), r
    assert not r["painel-codificado"], r


@pytest.mark.parametrize(
    ("bloqueio", "falham"),
    [
        # Bloqueia <img>, mas <svg> e <details> passam; o painel continua sem limpeza nenhuma.
        (r'_TAG_SCRIPT = re.compile(r"</?(script|img)[^>]*>", re.IGNORECASE)', BUSCA[1:] + PAINEL),
        # Tira atributos on...= com aspas; sem aspas o atributo sobrevive.
        (
            r"""_TAG_SCRIPT = re.compile(r'</?script[^>]*>|\son\w+="[^"]*"', re.IGNORECASE)""",
            BUSCA + PAINEL,
        ),
    ],
)
def test_blocklists_are_rejected(runtime: tuple[Any, Any], bloqueio: str, falham: tuple[str, ...]) -> None:
    rt, ev = runtime
    lab, _, servico = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, servico, BLOQUEIO_ORIGINAL, bloqueio)
    r = lab.evaluate(ev, ref)
    assert r["busca-legitima"], r
    assert not any(r[k] for k in falham), r


@pytest.mark.parametrize("r", XSS_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: XssRamo) -> None:
    ramo = r.ramo
    expected = {
        f"xss/answer/locate-cleaner-{ramo}-v1": "limpar_texto",
        f"xss/answer/safe-filter-{ramo}-v1": "safe",
        f"xss/answer/client-cookie-{ramo}-v1": r.cookie_comum,
        f"xss/answer/staff-cookie-{ramo}-v1": r.cookie_equipe,
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
