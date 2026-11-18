"""Suíte da família cors (LAB-029..031) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa liberar no CORS só origens de uma lista confiável, e reprovar: o código original
(reflete qualquer origem com credenciais), uma correção que só tira o Allow-Credentials mas segue
refletindo a origem, e uma que usa o curinga ``*`` (não serve com credenciais e quebra a origem confiável).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import CORS_RAMOS, CorsRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-029-cors-corretora", "lab-029-cors"),
    "sau": ("LAB-030-cors-saude", "lab-030-cors"),
    "ind": ("LAB-031-cors-energia", "lab-031-cors"),
}
SERVICO = "/workspace/services/cors_service.py"

VULN = (
    "    def cabecalhos(self, origem: str) -> dict[str, str]:\n"
    '        """Monta os cabeçalhos CORS da resposta da API, a partir da origem que veio na requisição."""\n'
    "        if not origem:\n"
    "            return {}\n"
    "        # Reflete a origem recebida, seja ela qual for, e ainda libera o envio de credenciais.\n"
    "        return {\n"
    '            "Access-Control-Allow-Origin": origem,\n'
    '            "Access-Control-Allow-Credentials": "true",\n'
    "        }\n"
)
CORRETO = (
    "    # Origens que podem ler a API pelo navegador (o próprio portal). Ajuste conforme o ambiente.\n"
    '    ORIGENS_CONFIAVEIS = ("https://portal.exemplo",)\n\n'
    "    def cabecalhos(self, origem: str) -> dict[str, str]:\n"
    '        """Monta os cabeçalhos CORS da resposta da API, a partir da origem que veio na requisição."""\n'
    "        if origem not in self.ORIGENS_CONFIAVEIS:\n"
    "            return {}\n"
    "        return {\n"
    '            "Access-Control-Allow-Origin": origem,\n'
    '            "Access-Control-Allow-Credentials": "true",\n'
    "        }\n"
)
# Tira o Allow-Credentials, mas segue refletindo qualquer origem: a origem maliciosa ainda é liberada.
SO_CREDENCIAIS = (
    "    def cabecalhos(self, origem: str) -> dict[str, str]:\n"
    '        """Monta os cabeçalhos CORS da resposta da API, a partir da origem que veio na requisição."""\n'
    "        if not origem:\n"
    "            return {}\n"
    '        return {"Access-Control-Allow-Origin": origem}\n'
)
# Curinga: não restringe por origem e, com credenciais, nem é aceito pelo navegador.
CURINGA = (
    "    def cabecalhos(self, origem: str) -> dict[str, str]:\n"
    '        """Monta os cabeçalhos CORS da resposta da API, a partir da origem que veio na requisição."""\n'
    "        if not origem:\n"
    "            return {}\n"
    "        return {\n"
    '            "Access-Control-Allow-Origin": "*",\n'
    '            "Access-Control-Allow-Credentials": "true",\n'
    "        }\n"
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
def test_original_code_reflects_any_origin(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # A API devolve os dados e libera a origem confiável, mas reflete a maliciosa e libera credenciais.
    assert r["perfil-dados"] and r["origem-confiavel-liberada"], r
    assert not r["origem-maliciosa-sem-reflexo"], r
    assert not r["credenciais-nao-liberadas"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_allowlist_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_dropping_credentials_still_reflects_origin(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_CREDENCIAIS)
    r = lab.evaluate(ev, ref)
    # Sem credenciais, mas ainda reflete a origem maliciosa: reprovado.
    assert r["credenciais-nao-liberadas"], r
    assert not r["origem-maliciosa-sem-reflexo"], r


def test_wildcard_breaks_trusted_origin_and_keeps_credentials(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CURINGA)
    r = lab.evaluate(ev, ref)
    # Curinga não ecoa a origem confiável e segue liberando credenciais: reprovado.
    assert not r["origem-confiavel-liberada"], r
    assert not r["credenciais-nao-liberadas"], r


@pytest.mark.parametrize("r", CORS_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: CorsRamo) -> None:
    expected = {
        f"cors/answer/metodo-{r.ramo}-v1": "cabecalhos",
        f"cors/answer/reflete-{r.ramo}-v1": "reflete",
        f"cors/answer/defesa-{r.ramo}-v1": "lista",
        f"cors/answer/credenciais-{r.ramo}-v1": "credenciais",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
