"""Suítes das famílias mobile (LAB-050..067, ADR-025) contra Docker real. Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

Para cada lab: o código original reprova e a correção da etapa 5 passa. Correções parciais comuns
também reprovam: só exigir token sem conferir a conta (MOB-01), guardar hash da senha (MOB-02), só
checar se o cabeçalho da prova veio (MOB-04) e tirar só o documento da resposta (MOB-08).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer
from app.validation.suites_familias import MOB_RAMOS, MobRamo

from tests.docker_support import docker_lab_image, lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

# (família, ramo) -> (pasta do lab, nome da imagem)
LABS = {
    ("mob-chave-embutida", "fin"): ("LAB-050-mob-chave-embutida-fintech", "lab-050-mobile"),
    ("mob-chave-embutida", "sau"): ("LAB-051-mob-chave-embutida-saude", "lab-051-mobile"),
    ("mob-chave-embutida", "ind"): ("LAB-052-mob-chave-embutida-industria", "lab-052-mobile"),
    ("mob-dados-locais", "fin"): ("LAB-053-mob-dados-locais-fintech", "lab-053-mobile"),
    ("mob-dados-locais", "sau"): ("LAB-054-mob-dados-locais-saude", "lab-054-mobile"),
    ("mob-dados-locais", "ind"): ("LAB-055-mob-dados-locais-industria", "lab-055-mobile"),
    ("mob-biometria-cliente", "fin"): ("LAB-056-mob-biometria-cliente-fintech", "lab-056-mobile"),
    ("mob-biometria-cliente", "sau"): ("LAB-057-mob-biometria-cliente-saude", "lab-057-mobile"),
    ("mob-biometria-cliente", "ind"): ("LAB-058-mob-biometria-cliente-industria", "lab-058-mobile"),
    ("mob-sessao-logout", "fin"): ("LAB-059-mob-sessao-logout-fintech", "lab-059-mobile"),
    ("mob-sessao-logout", "sau"): ("LAB-060-mob-sessao-logout-saude", "lab-060-mobile"),
    ("mob-sessao-logout", "ind"): ("LAB-061-mob-sessao-logout-industria", "lab-061-mobile"),
    ("mob-dados-demais", "fin"): ("LAB-062-mob-dados-demais-fintech", "lab-062-mobile"),
    ("mob-dados-demais", "sau"): ("LAB-063-mob-dados-demais-saude", "lab-063-mobile"),
    ("mob-dados-demais", "ind"): ("LAB-064-mob-dados-demais-industria", "lab-064-mobile"),
    ("mob-modo-teste", "fin"): ("LAB-065-mob-modo-teste-fintech", "lab-065-mobile"),
    ("mob-modo-teste", "sau"): ("LAB-066-mob-modo-teste-saude", "lab-066-mobile"),
    ("mob-modo-teste", "ind"): ("LAB-067-mob-modo-teste-industria", "lab-067-mobile"),
}
FOCO = {
    "mob-chave-embutida": "/workspace/services/acesso_service.py",
    "mob-dados-locais": "/workspace/dispositivo/sessao_local.py",
    "mob-biometria-cliente": "/workspace/services/acao_service.py",
    "mob-sessao-logout": "/workspace/services/sessao_service.py",
    "mob-dados-demais": "/workspace/services/perfil_service.py",
    "mob-modo-teste": "/workspace/services/identidade_service.py",
}
VULN = {
    "mob-chave-embutida": (
        "        # O app envia a chave que vem no pacote; o servidor aceita essa chave para QUALQUER conta.\n"
        "        return chave == self._chave_do_app\n"
    ),
    "mob-dados-locais": (
        "        # Guarda tudo o que o login usou, em texto puro, nas preferências do app.\n"
        '        self._gravar({"login": login, "senha": senha, "token": token})\n'
    ),
    "mob-biometria-cliente": (
        "        # A digital só é pedida na tela do app; o servidor executa sem conferir prova nenhuma.\n"
        "        return self._registrar(conta_id)\n"
    ),
    "mob-sessao-logout": (
        "        # Só o app esquece o token; no servidor ele continua valendo.\n        return None\n"
    ),
    "mob-dados-demais": (
        "        # Devolve o registro inteiro da conta; a tela do app só mostra nome e resumo.\n"
        "        return self._repositorio.perfil_completo(conta_id)\n"
    ),
    "mob-modo-teste": (
        "        # Atalho de homologação: com X-Debug: 1 o app de testes entra como a conta 1, sem login.\n"
        '        if cabecalhos.get("X-Debug") == "1":\n'
        "            return 1\n"
        "        return self._tokens.conta_do_token(token) if token else None\n"
    ),
}
CORRETO = {
    "mob-chave-embutida": (
        "        # Exige o token do usuário (emitido no login) e confere que a conta pedida é a dele.\n"
        "        dono = self._tokens.conta_do_token(token) if token else None\n"
        "        return dono is not None and dono == conta_id\n"
    ),
    "mob-dados-locais": (
        "        # Guarda só o necessário para manter a sessão: nunca a senha.\n"
        '        self._gravar({"login": login, "token": token})\n'
    ),
    "mob-biometria-cliente": (
        "        # O servidor exige a prova da digital, emitida para ESTA conta há menos de 60 s.\n"
        "        if not prova or not self._provas.valida(prova, conta_id):\n"
        '            raise PermissionError("autenticacao recente exigida")\n'
        "        return self._registrar(conta_id)\n"
    ),
    "mob-sessao-logout": (
        "        # Revoga o token no servidor: depois do logout ele não abre mais nada.\n"
        "        self._tokens.revogar(token)\n"
    ),
    "mob-dados-demais": (
        "        # Devolve só o que a tela usa (minimização): nome e resumo.\n"
        "        perfil = self._repositorio.perfil_completo(conta_id)\n"
        '        return {"nome": perfil["nome"], "resumo": perfil["resumo"]}\n'
    ),
    "mob-modo-teste": (
        "        # Sem atalho de teste em produção: só o token emitido no login identifica o usuário.\n"
        "        return self._tokens.conta_do_token(token) if token else None\n"
    ),
}
# Correções parciais que devem reprovar: (família, trecho, verificação que continua falhando).
PARCIAIS = [
    (
        "mob-chave-embutida",
        "        return self._tokens.conta_do_token(token) is not None if token else False\n",
        "outra-conta-negada",
    ),
    (
        "mob-dados-locais",
        "        import hashlib\n"
        "        resumo = hashlib.sha256(senha.encode()).hexdigest()\n"
        '        self._gravar({"login": login, "senha_hash": resumo, "token": token})\n',
        "sem-chave-de-senha",
    ),
    (
        "mob-biometria-cliente",
        "        if not prova:\n"
        '            raise PermissionError("autenticacao recente exigida")\n'
        "        return self._registrar(conta_id)\n",
        "prova-falsa-negada",
    ),
    (
        "mob-dados-demais",
        "        perfil = self._repositorio.perfil_completo(conta_id)\n"
        '        perfil.pop("documento")\n'
        "        return perfil\n",
        "sem-dados-pessoais",
    ),
]


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


def _lab(fam: str, ramo: str) -> LabUnderTest:
    lab_dir, name = LABS[(fam, ramo)]
    return LabUnderTest(lab_dir, lab_image(lab_dir, f"cecyber-labs/{name}:local"))


@pytest.mark.parametrize(("fam", "ramo"), sorted(LABS))
def test_original_fails_and_fix_passes(runtime: tuple[Any, Any], fam: str, ramo: str) -> None:
    rt, ev = runtime
    lab = _lab(fam, ramo)
    # Cada provisão cria uma rede Docker: encerra logo após avaliar, para não esgotar o pool de redes.
    _, ref = lab.provision(rt)
    try:
        original = lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)
    assert not all(original.values()), original
    box, ref2 = lab.provision(rt)
    try:
        replace_in_file(box, FOCO[fam], VULN[fam], CORRETO[fam])
        corrigido = lab.evaluate(ev, ref2)
    finally:
        rt.terminate(ref2)
    assert all(corrigido.values()), corrigido


@pytest.mark.parametrize(("fam", "parcial", "falha"), PARCIAIS, ids=[p[0] for p in PARCIAIS])
def test_partial_fixes_still_fail(runtime: tuple[Any, Any], fam: str, parcial: str, falha: str) -> None:
    rt, ev = runtime
    lab = _lab(fam, "fin")
    box, ref = lab.provision(rt)
    try:
        replace_in_file(box, FOCO[fam], VULN[fam], parcial)
        r = lab.evaluate(ev, ref)
    finally:
        rt.terminate(ref)
    assert not r[falha], r


RESPOSTAS = {
    "mob-chave-embutida": ("conta_autorizada", "sim", "token", "não"),
    "mob-dados-locais": ("guardar", "senha", "token", "não"),
    "mob-biometria-cliente": ("executar", "sim", "prova", "servidor"),
    "mob-sessao-logout": ("sair", "sim", "revogar", "não"),
    "mob-dados-demais": ("perfil", "sim", "minimização", "não"),
    "mob-modo-teste": ("identificar", "sim", "X-Debug", "não"),
}


@pytest.mark.parametrize("r", MOB_RAMOS, ids=lambda r: r.ramo)
def test_answer_suites_accept_documented_answers(r: MobRamo) -> None:
    for fam, respostas in RESPOSTAS.items():
        for etapa, resposta in zip(("metodo", "comportamento", "defesa", "onde"), respostas, strict=True):
            suite = get_suite(f"{fam}/answer/{etapa}-{r.ramo}-v1")
            assert isinstance(suite, AnswerSuite)
            assert normalize_answer(resposta) in {normalize_answer(a) for a in suite.accepted}
