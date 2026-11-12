from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from app.gateway.tickets import Audience, Purpose, TokenError, issue, verify

SECRET = "s" * 40
NOW = datetime(2026, 11, 12, 12, tzinfo=UTC)


def _ticket(**kw: object) -> str:
    args = dict(
        sid="sid-1", sub="user-1", purpose=Purpose.WORKSPACE, aud=Audience.TICKET, now=NOW, ttl_seconds=60
    )
    args.update(kw)
    token, _ = issue(SECRET, **args)  # type: ignore[arg-type]
    return token


def test_roundtrip() -> None:
    c = verify(SECRET, _ticket(), aud=Audience.TICKET, purpose=Purpose.WORKSPACE, now=NOW)
    assert (c.sid, c.sub, c.pur) == ("sid-1", "user-1", Purpose.WORKSPACE)


@pytest.mark.parametrize(
    "case",
    ["expired", "wrong_secret", "tampered", "wrong_purpose", "ticket_as_grant", "garbage", "empty"],
)
def test_rejections(case: str) -> None:
    token, aud, purpose, now, secret = _ticket(), Audience.TICKET, Purpose.WORKSPACE, NOW, SECRET
    if case == "expired":
        now = NOW + timedelta(seconds=60)
    elif case == "wrong_secret":
        secret = "x" * 40
    elif case == "tampered":
        payload, sig = token.split(".")
        token = payload[:-2] + ("AA" if payload[-2:] != "AA" else "BB") + "." + sig
    elif case == "wrong_purpose":
        purpose = Purpose.PREVIEW
    elif case == "ticket_as_grant":
        aud = Audience.GRANT
    elif case == "garbage":
        token = "abc"
    else:
        token = ""
    with pytest.raises(TokenError):
        verify(secret, token, aud=aud, purpose=purpose, now=now)


def test_each_ticket_has_unique_jti() -> None:
    _, a = issue(
        SECRET, sid="s", sub="u", purpose=Purpose.PREVIEW, aud=Audience.TICKET, now=NOW, ttl_seconds=5
    )
    _, b = issue(
        SECRET, sid="s", sub="u", purpose=Purpose.PREVIEW, aud=Audience.TICKET, now=NOW, ttl_seconds=5
    )
    assert a.jti != b.jti
