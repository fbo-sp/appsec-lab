"""Suíte da família path-traversal (LAB-032..034) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa garantir que o caminho final do documento fique dentro da pasta base, e reprovar:
o código original (abre qualquer caminho), uma correção que só bloqueia o texto ".." (deixa passar
caminho absoluto) e uma que só bloqueia caminho absoluto (deixa passar ../).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import PATH_RAMOS, PathRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-032-path-corretora", "lab-032-path"),
    "sau": ("LAB-033-path-saude", "lab-033-path"),
    "ind": ("LAB-034-path-energia", "lab-034-path"),
}
SERVICO = "/workspace/services/documento_service.py"

VULN = (
    "    def ler(self, nome: str) -> str:\n"
    '        """Lê o documento de nome ``nome`` dentro da pasta de documentos e devolve o conteúdo."""\n'
    "        caminho = os.path.join(self.BASE, nome)\n"
    '        with open(caminho, encoding="utf-8") as arquivo:\n'
    "            return arquivo.read()\n"
)
CORRETO = (
    "    def ler(self, nome: str) -> str:\n"
    '        """Lê o documento de nome ``nome`` dentro da pasta de documentos e devolve o conteúdo."""\n'
    "        base = os.path.realpath(self.BASE)\n"
    "        caminho = os.path.realpath(os.path.join(base, nome))\n"
    "        if caminho != base and not caminho.startswith(base + os.sep):\n"
    '            raise ValueError("Documento não permitido.")\n'
    '        with open(caminho, encoding="utf-8") as arquivo:\n'
    "            return arquivo.read()\n"
)
# Bloqueia só o texto "..": caminho absoluto continua escapando.
SO_DOTDOT = (
    "    def ler(self, nome: str) -> str:\n"
    '        """Lê o documento de nome ``nome`` dentro da pasta de documentos e devolve o conteúdo."""\n'
    '        if ".." in nome:\n'
    '            raise ValueError("Documento não permitido.")\n'
    "        caminho = os.path.join(self.BASE, nome)\n"
    '        with open(caminho, encoding="utf-8") as arquivo:\n'
    "            return arquivo.read()\n"
)
# Bloqueia só caminho absoluto: ../ continua escapando.
SO_ABSOLUTO = (
    "    def ler(self, nome: str) -> str:\n"
    '        """Lê o documento de nome ``nome`` dentro da pasta de documentos e devolve o conteúdo."""\n'
    '        if nome.startswith("/"):\n'
    '            raise ValueError("Documento não permitido.")\n'
    "        caminho = os.path.join(self.BASE, nome)\n"
    '        with open(caminho, encoding="utf-8") as arquivo:\n'
    "            return arquivo.read()\n"
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
def test_original_code_allows_traversal(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # Documento legítimo funciona, mas ../ e caminho absoluto leem arquivos de fora da pasta.
    assert r["documento-legitimo"], r
    assert not r["traversal-relativo-bloqueado"], r
    assert not r["traversal-absoluto-bloqueado"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_realpath_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_blocking_dotdot_only_still_allows_absolute(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_DOTDOT)
    r = lab.evaluate(ev, ref)
    # Barra ../, mas caminho absoluto continua lendo de fora: reprovado.
    assert r["traversal-relativo-bloqueado"], r
    assert not r["traversal-absoluto-bloqueado"], r


def test_blocking_absolute_only_still_allows_dotdot(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_ABSOLUTO)
    r = lab.evaluate(ev, ref)
    # Barra caminho absoluto, mas ../ continua lendo de fora: reprovado.
    assert r["traversal-absoluto-bloqueado"], r
    assert not r["traversal-relativo-bloqueado"], r


@pytest.mark.parametrize("r", PATH_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: PathRamo) -> None:
    expected = {
        f"path-traversal/answer/metodo-{r.ramo}-v1": "ler",
        f"path-traversal/answer/saiu-{r.ramo}-v1": "saiu",
        f"path-traversal/answer/absoluto-{r.ramo}-v1": "absoluto",
        f"path-traversal/answer/regra-{r.ramo}-v1": "dentro",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
