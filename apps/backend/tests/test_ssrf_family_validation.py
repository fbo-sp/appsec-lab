"""Suíte da família ssrf (LAB-020..022) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa aprovar uma lista de permissão (allowlist) de destino validada no servidor, e reprovar:
o código original (busca qualquer URL), uma blocklist por string que só barra a porta do console (deixa
``file://`` passar) e uma blocklist que barra todo loopback (quebra a busca legítima, que também é loopback).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import SSRF_RAMOS, SsrfRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-020-ssrf-cooperativa", "lab-020-ssrf"),
    "sau": ("LAB-021-ssrf-clinica", "lab-021-ssrf"),
    "ind": ("LAB-022-ssrf-siderurgica", "lab-022-ssrf"),
}
SERVICO = "/workspace/services/importador_service.py"

IMPORT = "import urllib.request\n"
IMPORT_NOVO = "import urllib.parse\nimport urllib.request\n"

METODO = (
    "    def importar(self, url: str) -> str:\n"
    '        """Busca o documento na URL informada e devolve o conteúdo para a prévia."""\n'
    "        if not url:\n"
    '            raise ValueError("Informe a URL do documento.")\n'
    "        # Abre a URL que veio no formulário e devolve o conteúdo buscado.\n"
    "        with urllib.request.urlopen(url, timeout=3) as resposta:  # noqa: S310\n"
    '            return resposta.read().decode("utf-8", "replace")[:4000]\n'
)
CORRETO = (
    "    # Único destino que o importador pode acessar (o Serviço de Documentos interno).\n"
    '    PERMITIDO = ("http", "127.0.0.1", 8090)\n\n'
    "    def importar(self, url: str) -> str:\n"
    '        """Busca o documento na URL informada e devolve o conteúdo para a prévia."""\n'
    "        if not url:\n"
    '            raise ValueError("Informe a URL do documento.")\n'
    "        partes = urllib.parse.urlsplit(url)\n"
    "        destino = (partes.scheme, partes.hostname, partes.port or 80)\n"
    "        if destino != self.PERMITIDO:\n"
    '            raise ValueError("Destino não permitido: o importador só acessa o Serviço de Documentos.")\n'
    "        with urllib.request.urlopen(url, timeout=3) as resposta:  # noqa: S310\n"
    '            return resposta.read().decode("utf-8", "replace")[:4000]\n'
)
# Blocklist frágil: barra só a porta do console por string; file:// continua passando.
BLOCKLIST_STRING = (
    "    def importar(self, url: str) -> str:\n"
    '        """Busca o documento na URL informada e devolve o conteúdo para a prévia."""\n'
    "        if not url:\n"
    '            raise ValueError("Informe a URL do documento.")\n'
    '        if "9000" in url:\n'
    '            raise ValueError("Destino não permitido.")\n'
    "        with urllib.request.urlopen(url, timeout=3) as resposta:  # noqa: S310\n"
    '            return resposta.read().decode("utf-8", "replace")[:4000]\n'
)
# Blocklist de loopback: barra o console, mas também o documento legítimo (que também é loopback).
BLOCKLIST_LOOPBACK = (
    "    def importar(self, url: str) -> str:\n"
    '        """Busca o documento na URL informada e devolve o conteúdo para a prévia."""\n'
    "        if not url:\n"
    '            raise ValueError("Informe a URL do documento.")\n'
    '        if "127.0.0.1" in url or "localhost" in url:\n'
    '            raise ValueError("Destino não permitido.")\n'
    "        with urllib.request.urlopen(url, timeout=3) as resposta:  # noqa: S310\n"
    '            return resposta.read().decode("utf-8", "replace")[:4000]\n'
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


def _corrigir(box: Any) -> None:
    replace_in_file(box, SERVICO, IMPORT, IMPORT_NOVO)
    replace_in_file(box, SERVICO, METODO, CORRETO)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_code_allows_ssrf(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # Documento legítimo funciona, mas o console interno e o file:// não são barrados.
    assert r["documento-legitimo"], r
    assert not r["console-interno-bloqueado"], r
    assert not r["esquema-arquivo-bloqueado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_allowlist_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    _corrigir(box)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_string_blocklist_still_allows_file_scheme(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, METODO, BLOCKLIST_STRING)
    r = lab.evaluate(ev, ref)
    # Barra o console (porta 9000), mas file:// continua passando: reprovado.
    assert r["documento-legitimo"] and r["console-interno-bloqueado"], r
    assert not r["esquema-arquivo-bloqueado"], r


def test_loopback_blocklist_breaks_legitimate_fetch(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, METODO, BLOCKLIST_LOOPBACK)
    r = lab.evaluate(ev, ref)
    # Barra todo loopback: o console cai, mas a busca legítima (também loopback) também cai.
    assert not r["documento-legitimo"], r


@pytest.mark.parametrize("r", SSRF_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: SsrfRamo) -> None:
    expected = {
        f"ssrf/answer/funcao-busca-{r.ramo}-v1": "urlopen",
        f"ssrf/answer/credencial-vazada-{r.ramo}-v1": r.meta_chave,
        f"ssrf/answer/destino-legitimo-{r.ramo}-v1": "127.0.0.1:8090",
        f"ssrf/answer/defesa-{r.ramo}-v1": "allowlist",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
