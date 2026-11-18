"""Suíte da família pacote-assinatura (LAB-083..085) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa recalcular o HMAC do conteúdo canônico e comparar em tempo constante antes de
aplicar, e a suíte reprova: o código original (aplica qualquer pacote) e uma correção que só exige o
campo ``assinatura`` (o pacote alterado com a assinatura antiga continua passando).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import PACOTE_RAMOS, PacoteRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-083-pacote-assinatura-banco", "lab-083-pacote-assinatura"),
    "sau": ("LAB-084-pacote-assinatura-saude", "lab-084-pacote-assinatura"),
    "ind": ("LAB-085-pacote-assinatura-industria", "lab-085-pacote-assinatura"),
}
ARQUIVO = "/workspace/services/pacote_service.py"
VULN = (
    '        """Lê o pacote recebido do fornecedor e aplica os parâmetros."""\n'
    "        pacote = self._ler(texto)\n"
)
CORRETO = (
    '        """Lê o pacote recebido, confere a assinatura do fornecedor e só então aplica os parâmetros."""\n'
    "        pacote = self._ler(texto)\n"
    "        esperada = hmac.new(self._chave, conteudo_canonico(pacote), hashlib.sha256).hexdigest()\n"
    '        if not hmac.compare_digest(esperada, str(pacote.get("assinatura", ""))):\n'
    '            raise PacoteInvalido("assinatura do fornecedor não confere.")\n'
)
SO_CAMPO = (
    VULN
    + '        if "assinatura" not in pacote:\n            raise PacoteInvalido("pacote sem assinatura.")\n'
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
def test_original_applies_tampered_package(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, None)
    assert r["pacote-legitimo-aplicado"], r
    assert not r["pacote-adulterado-recusado"], r
    assert not r["parametro-intacto"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_hmac_check_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    r = _avaliar(*runtime, ramo, CORRETO)
    assert all(r.values()), r


def test_field_presence_is_not_enough(runtime: tuple[Any, Any]) -> None:
    r = _avaliar(*runtime, "fin", SO_CAMPO)
    assert r["pacote-sem-assinatura-recusado"], r
    assert not r["pacote-adulterado-recusado"], r


@pytest.mark.parametrize("r", PACOTE_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: PacoteRamo) -> None:
    expected = {
        f"pacote-assinatura/answer/campo-{r.ramo}-v1": "assinatura",
        f"pacote-assinatura/answer/valor-{r.ramo}-v1": str(r.valor_mal),
        f"pacote-assinatura/answer/garantia-{r.ramo}-v1": "origem",
        f"pacote-assinatura/answer/metodo-{r.ramo}-v1": "importar",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}


def test_shipped_package_matches_suite_signature() -> None:
    """O pacote em pacotes_recebidos/ é o mesmo que a suíte assina (mesma chave e conteúdo canônico)."""
    import json
    from pathlib import Path

    from app.validation.suites_familias import _pacote_assinado

    raiz = Path(__file__).resolve().parents[3] / "laboratories"
    for r in PACOTE_RAMOS:
        (arquivo,) = (raiz / LABS[r.ramo][0] / "runtime/workspace/pacotes_recebidos").glob("*.json")
        assert json.loads(arquivo.read_text(encoding="utf-8")) == _pacote_assinado(r)
