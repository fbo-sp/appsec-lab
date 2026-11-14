"""Suíte do LAB-003 (JWT) contra Docker real (VAL-01/02). Opt-in: ``DOCKER_CONTRACT_TESTS=1``.

A verificação do token precisa aprovar correções corretas e reprovar a original e "correções" que só
barram ``alg: none``, ignoram a validade ou bloqueiam o gerente legítimo (ADR-010/ADR-015).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from app.validation.suites import AnswerSuite, get_suite, normalize_answer

from tests.docker_support import lab_image
from tests.lab_eval_support import LabUnderTest, replace_in_file

LAB_DIR = "LAB-003-jwt-cartoes"
TOKEN_SERVICE = "/workspace/services/token.service.js"
VULNERABLE = "  return jwt.decode(token);\n"
FIXES = {
    "verify-hs256": (
        "  try {\n"
        "    return jwt.verify(token, config.SEGREDO_JWT, { algorithms: ['HS256'] });\n"
        "  } catch (erro) {\n"
        "    return null;\n"
        "  }\n"
    ),
    "verify-sem-lista": (
        "  try {\n"
        "    return jwt.verify(token, config.SEGREDO_JWT);\n"
        "  } catch (erro) {\n"
        "    return null;\n"
        "  }\n"
    ),
    # Erradas:
    "so-barra-none": (
        "  const completo = jwt.decode(token, { complete: true });\n"
        "  if (!completo || completo.header.alg === 'none') return null;\n"
        "  return completo.payload;\n"
    ),
    "ignora-validade": (
        "  try {\n"
        "    return jwt.verify(token, config.SEGREDO_JWT, {\n"
        "      algorithms: ['HS256'], ignoreExpiration: true,\n"
        "    });\n"
        "  } catch (erro) {\n"
        "    return null;\n"
        "  }\n"
    ),
    "barra-admin": (
        "  const dados = jwt.decode(token);\n"
        "  if (dados && dados.perfil === 'admin') return null;\n"
        "  return dados;\n"
    ),
    "sintaxe-quebrada": (
        "  try {\n"
        "    return jwt.verify(token, config.SEGREDO_JWT;\n"
        "  } catch (erro) {\n"
        "    return null;\n"
        "  }\n"
    ),
}
SECURITY = ("sem-assinatura", "outra-chave", "token-adulterado", "token-expirado", "limite-forjado")


@pytest.fixture(scope="module")
def env() -> Iterator[tuple[Any, Any, LabUnderTest]]:
    lab = LabUnderTest(LAB_DIR, lab_image(LAB_DIR, "cecyber-labs/lab-003-jwt:local", base="node"))
    from app.runtime.docker_local import DockerRuntimeAdapter
    from app.validation.docker_eval import DockerEvaluator

    rt = DockerRuntimeAdapter()
    try:
        yield rt, DockerEvaluator(), lab
    finally:
        for owned in rt.list_owned():
            rt.terminate(owned.runtime_ref)


def test_original_code_trusts_forged_tokens(env: tuple[Any, Any, LabUnderTest]) -> None:
    rt, ev, lab = env
    _, ref = lab.provision(rt)
    r = lab.evaluate(ev, ref)
    assert r["cliente-ve-cartao"] and r["gerente-ve-painel"] and r["cliente-nao-e-gerente"], r
    assert not any(r[k] for k in SECURITY), r


@pytest.mark.parametrize("fix", ["verify-hs256", "verify-sem-lista"])
def test_correct_fixes_pass_every_check(env: tuple[Any, Any, LabUnderTest], fix: str) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, TOKEN_SERVICE, VULNERABLE, FIXES[fix])
    r = lab.evaluate(ev, ref)
    assert all(r.values()), r


@pytest.mark.parametrize(
    ("fix", "failing"),
    [
        ("so-barra-none", ("outra-chave", "token-adulterado", "token-expirado")),
        ("ignora-validade", ("token-expirado",)),
        ("barra-admin", ("gerente-ve-painel",)),
    ],
)
def test_incorrect_fixes_are_rejected(
    env: tuple[Any, Any, LabUnderTest], fix: str, failing: tuple[str, ...]
) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, TOKEN_SERVICE, VULNERABLE, FIXES[fix])
    r = lab.evaluate(ev, ref)
    assert not any(r[k] for k in failing), r


def test_syntax_error_reports_that_the_app_did_not_start(env: tuple[Any, Any, LabUnderTest]) -> None:
    rt, ev, lab = env
    box, ref = lab.provision(rt)
    replace_in_file(box, TOKEN_SERVICE, VULNERABLE, FIXES["sintaxe-quebrada"])
    out = lab.outcome(ev, ref)
    assert not out.app_started and not out.results
    assert "SyntaxError" in (out.app_log_tail or "")


def test_answer_suites_accept_documented_answers() -> None:
    expected = {
        "jwt/answer/locate-reader-v1": "lerToken",
        "jwt/answer/profile-claim-v1": "cliente",
        "jwt/answer/audit-code-v1": "ORB-AUD-5583-QX",
        "jwt/answer/limit-protocol-v1": "ORB-LIM-4821-50000",
    }
    for ref, answer in expected.items():
        suite = get_suite(ref)
        assert isinstance(suite, AnswerSuite)
        assert normalize_answer(answer) in {normalize_answer(a) for a in suite.accepted}
