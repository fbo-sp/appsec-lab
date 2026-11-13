"""IMP-401 a 405: validação de etapas, progresso, desbloqueio sequencial e dicas (OPEN-04).

Etapa ``answer`` é verificada no servidor; etapa ``http`` é avaliada pelo worker por meio do
EvaluatorPort (aqui o FakeEvaluator; a execução Docker real fica em test_docker_evaluator.py).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest
from app.db.models import AuditEvent, Job, StepSubmission
from app.runtime.factory import UnavailableEvaluator
from app.validation.port import EvaluationOutcome, EvaluationRequest, FakeEvaluator
from app.workers.provisioner import WorkerContext
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from tests.conftest import ALICE, BOB, create_session, drain


@pytest.fixture
def evaluator() -> FakeEvaluator:
    return FakeEvaluator()


@pytest.fixture
def wk(worker: WorkerContext, evaluator: FakeEvaluator) -> WorkerContext:
    return replace(worker, evaluator=evaluator)


def _ready(
    client: TestClient, wk: WorkerContext, headers: dict[str, str] = ALICE, key: str = "key-0000001"
) -> str:
    sid: str = create_session(client, headers, key=key).json()["sessionId"]
    drain(wk)
    return sid


def _steps(client: TestClient, sid: str, headers: dict[str, str] = ALICE) -> dict[str, Any]:
    r = client.get(f"/api/v1/sessions/{sid}/steps", headers=headers)
    assert r.status_code == 200, r.text
    body: dict[str, Any] = r.json()
    return body


def _evaluate(
    client: TestClient,
    sid: str,
    step: str,
    answer: str | None = None,
    key: str = "eval-0000001",
    headers: dict[str, str] = ALICE,
) -> Any:
    return client.post(
        f"/api/v1/sessions/{sid}/steps/{step}/evaluations",
        json={"answer": answer} if answer is not None else {},
        headers={**headers, "Idempotency-Key": key},
    )


def _hint(client: TestClient, sid: str, step: str, level: int, headers: dict[str, str] = ALICE) -> Any:
    return client.post(f"/api/v1/sessions/{sid}/steps/{step}/hints/{level}/reveal", headers=headers)


def _pass_explore(client: TestClient, sid: str) -> None:
    r = _evaluate(client, sid, "explore", "lab", key="eval-explore-ok")
    assert r.status_code == 202 and r.json()["status"] == "PASSED", r.text


# --- estado inicial e desbloqueio -----------------------------------------------------------------------


def test_initial_progress_first_step_available_rest_locked(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    body = _steps(client, _ready(client, wk))
    assert body["attempt"] == {**body["attempt"], "status": "IN_PROGRESS", "score": 0, "passingScore": 100}
    assert [(i["id"], i["status"]) for i in body["items"]] == [
        ("explore", "AVAILABLE"),
        ("edit-page", "LOCKED"),
    ]
    assert body["items"][0]["validation"] == {
        "type": "answer",
        "answerPrompt": "Usuário que executa o terminal",
    }


def test_locked_step_rejects_evaluation_and_hints(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    sid = _ready(client, wk)
    r = _evaluate(client, sid, "edit-page")
    assert r.status_code == 409 and r.json()["error"]["code"] == "STEP_LOCKED"
    r = _hint(client, sid, "edit-page", 1)
    assert r.status_code == 409 and r.json()["error"]["code"] == "STEP_LOCKED"


def test_wrong_answer_fails_without_unlocking_and_attempts_are_unlimited(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    sid = _ready(client, wk)
    for i in range(5):
        r = _evaluate(client, sid, "explore", "root", key=f"eval-wrong-{i:03d}")
        assert r.status_code == 202 and r.json()["status"] == "FAILED"
        assert r.json()["criteria"] == [
            {"id": "answer", "description": "Usuário que executa o terminal", "passed": False}
        ]
    item = _steps(client, sid)["items"][0]
    assert item["status"] == "AVAILABLE" and item["submissions"] == 5 and item["pointsAwarded"] == 0
    assert item["lastSubmission"]["status"] == "FAILED"
    _pass_explore(client, sid)  # OPEN-04: falhas anteriores não impedem nem penalizam


@pytest.mark.parametrize("answer", ["lab", "  LAB ", "10001"])
def test_correct_answer_passes_awards_points_and_unlocks_next(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext, answer: str
) -> None:
    sid = _ready(client, wk)
    r = _evaluate(client, sid, "explore", answer)
    assert r.status_code == 202 and r.json()["status"] == "PASSED"
    body = _steps(client, sid)
    assert body["attempt"]["score"] == 40
    assert [(i["id"], i["status"], i["pointsAwarded"]) for i in body["items"]] == [
        ("explore", "PASSED", 40),
        ("edit-page", "AVAILABLE", 0),
    ]
    assert body["items"][1]["task"] and body["items"][1]["validation"]["type"] == "http"
    r = _evaluate(client, sid, "explore", "lab", key="eval-again-001")
    assert r.status_code == 409 and r.json()["error"]["code"] == "STEP_ALREADY_PASSED"


def test_answer_step_requires_answer(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    sid = _ready(client, wk)
    r = _evaluate(client, sid, "explore", "   ")
    assert r.status_code == 400 and r.json()["error"]["code"] == "VALIDATION_ERROR"


# --- idempotência e autorização -----------------------------------------------------------------------


def test_evaluation_idempotency(client: TestClient, registered: dict[str, Any], wk: WorkerContext) -> None:
    sid = _ready(client, wk)
    a = _evaluate(client, sid, "explore", "root", key="eval-idem-0001")
    b = _evaluate(client, sid, "explore", "root", key="eval-idem-0001")
    assert b.status_code == 202 and b.headers["Idempotent-Replayed"] == "true"
    assert a.json()["evaluationId"] == b.json()["evaluationId"]
    assert _steps(client, sid)["items"][0]["submissions"] == 1
    c = _evaluate(client, sid, "explore", "lab", key="eval-idem-0001")
    assert c.status_code == 409 and c.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"
    assert _evaluate(client, sid, "explore", "lab", key="bad").status_code == 400


def test_other_user_cannot_see_or_submit(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    sid = _ready(client, wk)
    ev = _evaluate(client, sid, "explore", "root").json()["evaluationId"]
    assert _evaluate(client, sid, "explore", "lab", key="eval-bob-0001", headers=BOB).status_code == 404
    assert client.get(f"/api/v1/sessions/{sid}/evaluations/{ev}", headers=BOB).status_code == 404
    assert _hint(client, sid, "explore", 1, headers=BOB).status_code == 404
    assert client.get(f"/api/v1/sessions/{sid}/evaluations/{ev}", headers=ALICE).status_code == 200


def test_unknown_step_is_404(client: TestClient, registered: dict[str, Any], wk: WorkerContext) -> None:
    sid = _ready(client, wk)
    assert _evaluate(client, sid, "nope", "x").status_code == 404


def test_terminated_session_rejects_evaluation(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    sid = _ready(client, wk)
    assert client.delete(f"/api/v1/sessions/{sid}", headers=ALICE).status_code == 202
    r = _evaluate(client, sid, "explore", "lab")
    assert r.status_code == 409 and r.json()["error"]["code"] == "SESSION_NOT_READY"


# --- dicas (ADR-013: desconto por nível, teto de 10%) ------------------------------------------------


def test_hints_revealed_in_order_with_level_penalty(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext, session_factory: sessionmaker[Session]
) -> None:
    sid = _ready(client, wk)
    r = _hint(client, sid, "explore", 2)
    assert r.status_code == 409 and r.json()["error"]["code"] == "HINT_ORDER"
    assert _steps(client, sid)["items"][0]["hints"]["nextCost"] == 0
    h1 = _hint(client, sid, "explore", 1)
    assert h1.status_code == 200 and h1.json()["penalty"] == 0 and h1.json()["text"]
    assert _hint(client, sid, "explore", 1).json() == h1.json()  # revelar de novo é idempotente
    assert _steps(client, sid)["items"][0]["hints"]["nextCost"] == 1
    h2 = _hint(client, sid, "explore", 2)
    assert h2.status_code == 200 and h2.json()["penalty"] == 1
    assert _hint(client, sid, "explore", 2).json()["penalty"] == 0  # repetir não cobra de novo
    assert _hint(client, sid, "explore", 3).status_code == 404
    body = _steps(client, sid)
    item = body["items"][0]
    assert [(h["level"], h["cost"]) for h in item["hints"]["revealed"]] == [(1, 0), (2, 1)]
    # Antes de pontuar, o desconto não deixa a pontuação negativa.
    assert body["attempt"]["score"] == 0 and body["attempt"]["hintPenalty"] == 1
    _pass_explore(client, sid)
    att = _steps(client, sid)["attempt"]
    assert att["score"] == 39 and att["earnedPoints"] == 40
    assert att["hintPenalty"] == 1 and att["hintPenaltyCap"] == 10 and att["hintsUsed"] == 2
    with session_factory() as db:
        n = db.execute(select(AuditEvent).where(AuditEvent.action == "hint.revealed")).scalars().all()
    assert sorted(e.event_metadata["penalty"] for e in n) == [0, 1]


# --- etapa http via worker ------------------------------------------------------------------------------


def _drain_eval(
    client: TestClient, sid: str, wk: WorkerContext, key: str = "eval-http-0001"
) -> dict[str, Any]:
    r = _evaluate(client, sid, "edit-page", key=key)
    assert r.status_code == 202 and r.json()["status"] == "QUEUED", r.text
    ev = r.json()["evaluationId"]
    drain(wk)
    out: dict[str, Any] = client.get(f"/api/v1/sessions/{sid}/evaluations/{ev}", headers=ALICE).json()
    return out


def test_http_step_passes_via_worker_and_completes_attempt(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext, evaluator: FakeEvaluator
) -> None:
    sid = _ready(client, wk)
    _pass_explore(client, sid)
    res = _drain_eval(client, sid, wk)
    assert res["status"] == "PASSED" and all(c["passed"] for c in res["criteria"])
    assert [c["id"] for c in res["criteria"]] == ["page-greeting", "page-still-served"]
    req = evaluator.calls[0]
    assert req.workspace_path and req.app_port == 8080 and req.runtime_ref
    body = _steps(client, sid)
    att = body["attempt"]
    assert att["status"] == "COMPLETED" and att["score"] == 100 and att["maxScore"] == 100
    assert att["completedAt"] and att["startedAt"] <= att["completedAt"]
    assert att["hintsUsed"] == 0 and att["submissions"] == 2


def test_http_step_failure_reports_criteria(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext, evaluator: FakeEvaluator
) -> None:
    sid = _ready(client, wk)
    _pass_explore(client, sid)
    evaluator.results = {"page-greeting": False}
    res = _drain_eval(client, sid, wk)
    assert res["status"] == "FAILED"
    assert {c["id"]: c["passed"] for c in res["criteria"]} == {
        "page-greeting": False,
        "page-still-served": True,
    }
    evaluator.results = {}
    assert _drain_eval(client, sid, wk, key="eval-http-0002")["status"] == "PASSED"


def test_app_that_does_not_start_gets_single_clear_message(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext, evaluator: FakeEvaluator
) -> None:
    sid = _ready(client, wk)
    _pass_explore(client, sid)
    evaluator.not_started_log = '  File "app.py", line 3\nSyntaxError: invalid syntax'
    res = _drain_eval(client, sid, wk)
    assert res["status"] == "FAILED"  # reprova (não é falha técnica), mas sem N falhas de segurança
    assert [c["id"] for c in res["criteria"]] == ["app-starts"]
    assert "não iniciou" in res["feedback"] and "SyntaxError" in res["feedback"]
    evaluator.not_started_log = None
    assert _drain_eval(client, sid, wk, key="eval-http-0002")["status"] == "PASSED"


def test_only_one_pending_evaluation_per_session(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    sid = _ready(client, wk)
    _pass_explore(client, sid)
    assert _evaluate(client, sid, "edit-page", key="eval-pend-0001").status_code == 202
    r = _evaluate(client, sid, "edit-page", key="eval-pend-0002")
    assert r.status_code == 409 and r.json()["error"]["code"] == "EVALUATION_IN_PROGRESS"


class _Boom:
    def evaluate(self, request: EvaluationRequest) -> EvaluationOutcome:
        raise RuntimeError("docker down")


@pytest.mark.parametrize("make", [lambda: _Boom(), lambda: UnavailableEvaluator(), lambda: None])
def test_technical_failure_is_error_never_pass_or_fail(
    client: TestClient,
    registered: dict[str, Any],
    wk: WorkerContext,
    session_factory: sessionmaker[Session],
    make: Any,
) -> None:
    sid = _ready(client, wk)
    _pass_explore(client, sid)
    broken = replace(wk, evaluator=make())
    r = _evaluate(client, sid, "edit-page")
    drain(broken)
    res = client.get(f"/api/v1/sessions/{sid}/evaluations/{r.json()['evaluationId']}", headers=ALICE).json()
    assert res["status"] == "ERROR" and "falha técnica" in res["feedback"]
    item = _steps(client, sid)["items"][1]
    assert item["status"] == "AVAILABLE" and item["pointsAwarded"] == 0
    with session_factory() as db:
        sub = db.execute(select(StepSubmission).where(StepSubmission.status == "ERROR")).scalar_one()
        assert sub.error_code == "EVALUATION_ERROR"
        assert all(j.status == "succeeded" for j in db.execute(select(Job)).scalars() if j.kind == "EVALUATE")


def test_progress_survives_new_session(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    """Progresso pertence à tentativa (ADR-005): nova sessão do mesmo aluno retoma a etapa."""
    sid = _ready(client, wk)
    _pass_explore(client, sid)
    assert client.delete(f"/api/v1/sessions/{sid}", headers=ALICE).status_code == 202
    drain(wk)
    sid2 = _ready(client, wk, key="key-0000002")
    body = _steps(client, sid2)
    assert [i["status"] for i in body["items"]] == ["PASSED", "AVAILABLE"] and body["attempt"]["score"] == 40


def test_evaluation_history_is_owner_only_and_newest_first(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext, clock: Any
) -> None:
    sid = _ready(client, wk)
    _evaluate(client, sid, "explore", "root", key="eval-hist-0001")
    clock.advance(seconds=5)
    _pass_explore(client, sid)
    r = client.get(f"/api/v1/sessions/{sid}/evaluations", headers=ALICE)
    assert r.status_code == 200
    items = r.json()["items"]
    assert [i["status"] for i in items] == ["PASSED", "FAILED"]
    assert items[0]["stepId"] == "explore" and items[0]["stepTitle"] and items[0]["stepOrder"] == 1
    assert "answer" not in items[0]
    assert client.get(f"/api/v1/sessions/{sid}/evaluations", headers=BOB).status_code == 404


def test_rich_content_references_and_wrap_up_are_exposed(client: TestClient, wk: WorkerContext) -> None:
    from tests.conftest import ADMIN, benign_manifest

    m = benign_manifest()
    m["metadata"]["version"] = "0.9.0"
    ref = {"title": "CWE-89", "url": "https://cwe.mitre.org/data/definitions/89.html"}
    m["steps"][0]["task"] = "Rode `whoami` no terminal.\n\n```bash\nwhoami\n```"
    m["steps"][0]["references"] = [ref]
    m["learning"]["wrapUp"] = {"text": "Use **parâmetros**.", "references": [ref]}
    assert client.post("/api/v1/admin/lab-releases", json=m, headers=ADMIN).status_code == 201
    body = {"labId": "LAB-000", "version": "0.9.0", "variantId": "python-http"}
    sid = create_session(client, ALICE, body=body).json()["sessionId"]
    drain(wk)
    p = _steps(client, sid)
    first, locked = p["items"]
    assert first["task"].startswith("Rode `whoami`") and first["references"] == [ref]
    assert "references" not in locked  # etapa bloqueada não revela conteúdo
    assert p["wrapUp"] == {"text": "Use **parâmetros**.", "references": [ref]}


def test_progress_without_rich_content_has_empty_defaults(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext
) -> None:
    p = _steps(client, _ready(client, wk))
    assert p["items"][0]["references"] == [] and p["wrapUp"] is None


def test_resolution_metrics_count_active_minutes(
    client: TestClient, registered: dict[str, Any], wk: WorkerContext, evaluator: FakeEvaluator, clock: Any
) -> None:
    """ADR-014: o indicador do admin usa minutos ativos, não o tempo de calendário."""
    from tests.conftest import ADMIN

    sid = _ready(client, wk)
    _pass_explore(client, sid)  # validar é atividade (minuto 1)
    clock.advance(minutes=1)
    client.post(f"/api/v1/sessions/{sid}/activity", headers=ALICE)  # minuto 2
    clock.advance(minutes=8)  # parado
    assert _drain_eval(client, sid, wk)["status"] == "PASSED"  # minuto 3 e conclusão
    att = _steps(client, sid)["attempt"]
    assert att["status"] == "COMPLETED" and att["activeMinutes"] == 3 and att["sessions"] == 1
    assert client.get("/api/v1/admin/metrics/resolution", headers=ALICE).status_code == 403
    [item] = client.get("/api/v1/admin/metrics/resolution", headers=ADMIN).json()["items"]
    assert item["labId"] == "LAB-000" and item["completedAttempts"] == 1
    assert item["activeMinutes"]["p50"] == 3 and item["sessionsPerAttempt"] == 1
    assert item["calendarMinutesP50"] >= 9
