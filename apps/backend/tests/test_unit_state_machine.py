from __future__ import annotations

import itertools

import pytest
from app.sessions.state_machine import (
    ACTIVE,
    TERMINAL,
    TRANSITIONS,
    InvalidTransitionError,
    SessionEvent,
    SessionStatus,
    transition,
)

S, E = SessionStatus, SessionEvent


@pytest.mark.parametrize(("state", "event"), list(itertools.product(S, E)))
def test_every_pair_is_either_defined_or_rejected(state: SessionStatus, event: SessionEvent) -> None:
    if (state, event) in TRANSITIONS:
        assert transition(state, event) == TRANSITIONS[(state, event)]
    else:
        with pytest.raises(InvalidTransitionError):
            transition(state, event)


def test_terminal_states_have_no_exit() -> None:
    for state in TERMINAL:
        assert not [k for k in TRANSITIONS if k[0] == state]


def test_every_non_terminal_state_can_be_terminated() -> None:
    """docs/08 §3: qualquer estado não terminal aceita cancelamento (G-03)."""
    for state in set(S) - TERMINAL - {S.TERMINATING}:
        assert transition(state, E.REQUEST_TERMINATION) is S.TERMINATING


def test_active_states_can_expire() -> None:
    for state in ACTIVE:
        assert transition(state, E.EXPIRE) is S.EXPIRED


def test_every_state_reaches_terminated() -> None:
    graph: dict[SessionStatus, set[SessionStatus]] = {}
    for (src, _), dst in TRANSITIONS.items():
        graph.setdefault(src, set()).add(dst)
    for start in S:
        seen, stack = {start}, [start]
        while stack:
            for nxt in graph.get(stack.pop(), set()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        assert S.TERMINATED in seen, start


def test_validating_is_not_a_persisted_state() -> None:
    assert "VALIDATING" not in {s.value for s in S}


def test_happy_path() -> None:
    s = S.REQUESTED
    for ev in (
        E.START_PROVISIONING,
        E.RUNTIME_READY,
        E.FIRST_CONNECTION,
        E.COMPLETE,
        E.REQUEST_TERMINATION,
        E.RUNTIME_GONE,
    ):
        s = transition(s, ev)
    assert s is S.TERMINATED
