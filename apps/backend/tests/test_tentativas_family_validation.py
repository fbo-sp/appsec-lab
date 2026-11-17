"""Suíte da família tentativas-login (LAB-026..028) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa limitar as tentativas de login POR USUÁRIO, no servidor, e reprovar: o código
original (tentativas ilimitadas), uma correção que só conta/registra mas nunca bloqueia, e uma que
usa um contador GLOBAL (bloqueia também um usuário diferente que nunca errou a senha).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import TENTATIVAS_RAMOS, TentativasRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-026-tentativas-fintech", "lab-026-login"),
    "sau": ("LAB-027-tentativas-saude", "lab-027-login"),
    "ind": ("LAB-028-tentativas-industria", "lab-028-login"),
}
SERVICO = "/workspace/services/auth_service.py"

VULN = (
    "    def autenticar(self, login: str, senha: str) -> Conta | None:\n"
    '        """Confere login e senha e devolve a conta (ou None se não baterem)."""\n'
    "        encontrado = self._repositorio.buscar_por_login(login.strip().lower())\n"
    "        if encontrado is None:\n"
    "            return None\n"
    "        conta, senha_hash = encontrado\n"
    "        if check_password_hash(senha_hash, senha):\n"
    "            return conta\n"
    "        return None\n"
)
CORRETO = (
    "    # Quantas tentativas seguidas de login são permitidas por usuário antes de bloquear.\n"
    "    LIMITE = 5\n"
    "    _tentativas: dict[str, int] = {}\n\n"
    "    def autenticar(self, login: str, senha: str) -> Conta | None:\n"
    '        """Confere login e senha e devolve a conta (ou None se não baterem)."""\n'
    "        chave = login.strip().lower()\n"
    "        if self._tentativas.get(chave, 0) >= self.LIMITE:\n"
    '            raise ValueError("Muitas tentativas de login. Tente novamente mais tarde.")\n'
    "        encontrado = self._repositorio.buscar_por_login(chave)\n"
    "        if encontrado is not None:\n"
    "            conta, senha_hash = encontrado\n"
    "            if check_password_hash(senha_hash, senha):\n"
    "                self._tentativas[chave] = 0\n"
    "                return conta\n"
    "        self._tentativas[chave] = self._tentativas.get(chave, 0) + 1\n"
    "        return None\n"
)
# Conta as falhas mas nunca bloqueia: a força bruta continua possível.
SO_CONTA = (
    "    _tentativas: dict[str, int] = {}\n\n"
    "    def autenticar(self, login: str, senha: str) -> Conta | None:\n"
    '        """Confere login e senha e devolve a conta (ou None se não baterem)."""\n'
    "        chave = login.strip().lower()\n"
    "        encontrado = self._repositorio.buscar_por_login(chave)\n"
    "        if encontrado is not None:\n"
    "            conta, senha_hash = encontrado\n"
    "            if check_password_hash(senha_hash, senha):\n"
    "                self._tentativas[chave] = 0\n"
    "                return conta\n"
    "        self._tentativas[chave] = self._tentativas.get(chave, 0) + 1\n"
    "        return None\n"
)
# Contador GLOBAL (não por usuário): bloqueia também um usuário diferente que nunca errou.
GLOBAL = (
    "    LIMITE = 5\n"
    "    _total = 0\n\n"
    "    def autenticar(self, login: str, senha: str) -> Conta | None:\n"
    '        """Confere login e senha e devolve a conta (ou None se não baterem)."""\n'
    "        if AuthService._total >= self.LIMITE:\n"
    '            raise ValueError("Muitas tentativas de login. Tente novamente mais tarde.")\n'
    "        encontrado = self._repositorio.buscar_por_login(login.strip().lower())\n"
    "        if encontrado is not None:\n"
    "            conta, senha_hash = encontrado\n"
    "            if check_password_hash(senha_hash, senha):\n"
    "                return conta\n"
    "        AuthService._total += 1\n"
    "        return None\n"
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
def test_original_code_never_blocks(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    # Tentativas erradas são recusadas, mas o login nunca bloqueia: a sexta tentativa não trava.
    assert all(r[f"erro-{n}"] for n in range(1, 6)), r
    assert not r["bloqueio-apos-limite"], r
    assert r["login-legitimo"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_per_user_limit_fix_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, CORRETO)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_counting_without_blocking_still_allows_brute_force(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, SO_CONTA)
    r = lab.evaluate(ev, ref)
    # Conta as falhas, mas nunca bloqueia: a sexta tentativa ainda passa. Reprovado.
    assert not r["bloqueio-apos-limite"], r


def test_global_counter_blocks_innocent_user(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, VULN, GLOBAL)
    r = lab.evaluate(ev, ref)
    # Bloqueia depois do limite, mas o contador é global: um usuário diferente também trava. Reprovado.
    assert r["bloqueio-apos-limite"], r
    assert not r["login-legitimo"], r


@pytest.mark.parametrize("r", TENTATIVAS_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: TentativasRamo) -> None:
    expected = {
        f"tentativas-login/answer/metodo-{r.ramo}-v1": "autenticar",
        f"tentativas-login/answer/comportamento-{r.ramo}-v1": "continua",
        f"tentativas-login/answer/defesa-{r.ramo}-v1": "tentativas",
        f"tentativas-login/answer/onde-{r.ramo}-v1": "servidor",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
