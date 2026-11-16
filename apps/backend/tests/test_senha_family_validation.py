"""Suíte da família senha (LAB-017..019) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A correção precisa aprovar a adoção de um hash forte do werkzeug com migração no login, e reprovar o
código original (MD5), uma correção que confere mas não migra (hashes seguem em MD5) e a troca ingênua
para ``check_password_hash`` sem tratar o formato legado (tranca as contas antigas).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import SENHA_RAMOS, SenhaRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LABS = {
    "fin": ("LAB-017-senha-cooperativa", "lab-017-senha"),
    "sau": ("LAB-018-senha-laboratorio", "lab-018-senha"),
    "ind": ("LAB-019-senha-siderurgica", "lab-019-senha"),
}
SERVICO = "/workspace/services/auth_service.py"

IMPORT = "import hashlib\n\nfrom models.usuario import Usuario\n"
IMPORT_NOVO = (
    "import hashlib\n"
    "import hmac\n\n"
    "from werkzeug.security import check_password_hash, generate_password_hash\n\n"
    "from models.usuario import Usuario\n"
)
AUTENTICAR = (
    "    def autenticar(self, login: str, senha: str) -> Usuario | None:\n"
    "        encontrado = self._repositorio.buscar_por_login(login.strip().lower())\n"
    "        if encontrado is None:\n"
    "            return None\n"
    "        usuario, senha_hash = encontrado\n"
    "        # O usuário entra se o resumo da senha digitada for igual ao resumo guardado.\n"
    "        if self._resumo(senha) == senha_hash:\n"
    "            return usuario\n"
    "        return None\n"
)
CORRETO = (
    "    def autenticar(self, login: str, senha: str) -> Usuario | None:\n"
    "        encontrado = self._repositorio.buscar_por_login(login.strip().lower())\n"
    "        if encontrado is None:\n"
    "            return None\n"
    "        usuario, senha_hash = encontrado\n"
    '        if senha_hash.startswith(("scrypt:", "pbkdf2:")):\n'
    "            return usuario if check_password_hash(senha_hash, senha) else None\n"
    "        if not hmac.compare_digest(self._resumo(senha), senha_hash):\n"
    "            return None\n"
    "        self._repositorio.atualizar_senha(usuario.id, generate_password_hash(senha))\n"
    "        return usuario\n"
)
SEM_MIGRAR = (
    "    def autenticar(self, login: str, senha: str) -> Usuario | None:\n"
    "        encontrado = self._repositorio.buscar_por_login(login.strip().lower())\n"
    "        if encontrado is None:\n"
    "            return None\n"
    "        usuario, senha_hash = encontrado\n"
    '        if senha_hash.startswith(("scrypt:", "pbkdf2:")):\n'
    "            return usuario if check_password_hash(senha_hash, senha) else None\n"
    "        if hmac.compare_digest(self._resumo(senha), senha_hash):\n"
    "            return usuario\n"
    "        return None\n"
)
SO_WERKZEUG = (
    "    def autenticar(self, login: str, senha: str) -> Usuario | None:\n"
    "        encontrado = self._repositorio.buscar_por_login(login.strip().lower())\n"
    "        if encontrado is None:\n"
    "            return None\n"
    "        usuario, senha_hash = encontrado\n"
    "        return usuario if check_password_hash(senha_hash, senha) else None\n"
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
    replace_in_file(box, SERVICO, AUTENTICAR, CORRETO)


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_original_code_keeps_passwords_in_md5(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert r["login-legitimo"] and r["senha-errada-recusada"], r
    assert not r["hashes-migrados"], r


@pytest.mark.parametrize("ramo", sorted(LABS))
def test_strong_hash_with_migration_passes(runtime: tuple[Any, Any], ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(ramo)
    box, ref = lab.provision(rt)
    _corrigir(box)
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


def test_verifying_without_rehash_is_rejected(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("fin")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, IMPORT, IMPORT_NOVO)
    replace_in_file(box, SERVICO, AUTENTICAR, SEM_MIGRAR)
    r = lab.evaluate(ev, ref)
    assert r["login-legitimo"] and r["senha-errada-recusada"], r
    assert not r["hashes-migrados"], r  # confere, mas não regrava: contas seguem em MD5


def test_bare_check_password_hash_locks_out_legacy_accounts(runtime: tuple[Any, Any]) -> None:
    rt, ev = runtime
    lab = _lab("ind")
    box, ref = lab.provision(rt)
    replace_in_file(box, SERVICO, IMPORT, IMPORT_NOVO)
    replace_in_file(box, SERVICO, AUTENTICAR, SO_WERKZEUG)
    r = lab.evaluate(ev, ref)
    # check_password_hash não entende o hash legado (MD5): o login legítimo falha.
    assert not r["login-legitimo"] and not r["hashes-migrados"], r


@pytest.mark.parametrize("r", SENHA_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: SenhaRamo) -> None:
    expected = {
        f"senha/answer/hash-algo-{r.ramo}-v1": "md5",
        f"senha/answer/hash-repetido-{r.ramo}-v1": r.hash_repetido,
        f"senha/answer/hash-default-{r.ramo}-v1": "49c572f76b3c1d9172fe2a6b75f06cf0",
        f"senha/answer/funcao-werkzeug-{r.ramo}-v1": "generate_password_hash",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
