"""Máquina de estados da sessão (FR-021, docs/08 §3 com as correções G-03 de docs/22).

``VALIDATING`` não é persistido como estado de sessão: é projeção de UI derivada de
ValidationRun (docs/08 §3, esclarecimento). Estados terminais não possuem saída.
"""

from __future__ import annotations

from enum import StrEnum


class SessionStatus(StrEnum):
    REQUESTED = "REQUESTED"
    PROVISIONING = "PROVISIONING"
    READY = "READY"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"


class SessionEvent(StrEnum):
    START_PROVISIONING = "start_provisioning"
    RUNTIME_READY = "runtime_ready"
    FIRST_CONNECTION = "first_connection"
    COMPLETE = "complete"
    EXPIRE = "expire"
    FAIL = "fail"
    REQUEST_TERMINATION = "request_termination"
    RUNTIME_GONE = "runtime_gone"


S, E = SessionStatus, SessionEvent

TRANSITIONS: dict[tuple[SessionStatus, SessionEvent], SessionStatus] = {
    (S.REQUESTED, E.START_PROVISIONING): S.PROVISIONING,
    (S.REQUESTED, E.FAIL): S.FAILED,
    (S.REQUESTED, E.EXPIRE): S.EXPIRED,
    (S.REQUESTED, E.REQUEST_TERMINATION): S.TERMINATING,
    (S.PROVISIONING, E.RUNTIME_READY): S.READY,
    (S.PROVISIONING, E.FAIL): S.FAILED,
    (S.PROVISIONING, E.EXPIRE): S.EXPIRED,
    (S.PROVISIONING, E.REQUEST_TERMINATION): S.TERMINATING,
    (S.READY, E.FIRST_CONNECTION): S.ACTIVE,
    (S.READY, E.COMPLETE): S.COMPLETED,
    (S.READY, E.EXPIRE): S.EXPIRED,
    (S.READY, E.REQUEST_TERMINATION): S.TERMINATING,
    (S.ACTIVE, E.COMPLETE): S.COMPLETED,
    (S.ACTIVE, E.EXPIRE): S.EXPIRED,
    (S.ACTIVE, E.REQUEST_TERMINATION): S.TERMINATING,
    (S.COMPLETED, E.REQUEST_TERMINATION): S.TERMINATING,
    (S.FAILED, E.REQUEST_TERMINATION): S.TERMINATING,
    (S.EXPIRED, E.REQUEST_TERMINATION): S.TERMINATING,
    (S.TERMINATING, E.RUNTIME_GONE): S.TERMINATED,
}

TERMINAL: frozenset[SessionStatus] = frozenset({S.TERMINATED})
ACTIVE: frozenset[SessionStatus] = frozenset({S.REQUESTED, S.PROVISIONING, S.READY, S.ACTIVE})
EXPIRABLE: frozenset[SessionStatus] = ACTIVE
# Estados que exigem limpeza do runtime até chegar a TERMINATED.
NEEDS_CLEANUP: frozenset[SessionStatus] = frozenset({S.COMPLETED, S.EXPIRED, S.FAILED, S.TERMINATING})


class InvalidTransitionError(Exception):
    def __init__(self, current: SessionStatus, event: SessionEvent) -> None:
        super().__init__(f"Transição inválida: {current} --{event}-->")
        self.current = current
        self.event = event


def transition(current: SessionStatus, event: SessionEvent) -> SessionStatus:
    try:
        return TRANSITIONS[(current, event)]
    except KeyError:
        raise InvalidTransitionError(current, event) from None


def can(current: SessionStatus, event: SessionEvent) -> bool:
    return (current, event) in TRANSITIONS
