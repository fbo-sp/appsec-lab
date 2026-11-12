"""Tokens assinados (HMAC-SHA256) entre API e gateway de workspace (IMP-302, docs/13 §2).

Dois tipos, distinguidos pela audiência:
- ``ticket``: emitido pela API ao dono de uma sessão READY/ACTIVE; vida de segundos; uso único.
- ``grant``: emitido pelo gateway ao trocar um ticket válido; vai em cookie HttpOnly escopado.
Ambos carregam ``sid`` (sessão), ``sub`` (usuário) e ``pur`` (finalidade: workspace|preview).
Tokens nunca são registrados em log. Toda requisição no gateway revalida o estado no banco, de modo
que encerrar/expirar a sessão revoga o acesso imediatamente, mesmo com grant ainda não vencido.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Purpose(StrEnum):
    WORKSPACE = "workspace"
    PREVIEW = "preview"


class Audience(StrEnum):
    TICKET = "gateway-ticket"
    GRANT = "gateway-grant"


class TokenError(Exception):
    """Token ausente, malformado, adulterado, vencido ou de outra audiência/finalidade."""


@dataclass(frozen=True, slots=True)
class Claims:
    sid: str
    sub: str
    pur: Purpose
    aud: Audience
    exp: int
    jti: str


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _key(secret: str, aud: Audience) -> bytes:
    # Chaves derivadas por audiência: um ticket nunca é aceito como grant e vice-versa.
    return hmac.new(secret.encode(), f"cecyber-gateway:{aud.value}".encode(), hashlib.sha256).digest()


def issue(
    secret: str, *, sid: str, sub: str, purpose: Purpose, aud: Audience, now: datetime, ttl_seconds: int
) -> tuple[str, Claims]:
    claims = Claims(sid, sub, purpose, aud, int(now.timestamp()) + ttl_seconds, secrets.token_urlsafe(12))
    payload = _b64(
        json.dumps(
            {
                "sid": sid,
                "sub": sub,
                "pur": purpose.value,
                "aud": aud.value,
                "exp": claims.exp,
                "jti": claims.jti,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    )
    sig = _b64(hmac.new(_key(secret, aud), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}", claims


def verify(secret: str, token: str | None, *, aud: Audience, purpose: Purpose, now: datetime) -> Claims:
    if not token or token.count(".") != 1 or len(token) > 2048:
        raise TokenError("token ausente ou malformado")
    payload, sig = token.split(".")
    expected = _b64(hmac.new(_key(secret, aud), payload.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expected):
        raise TokenError("assinatura inválida")
    try:
        raw = json.loads(_unb64(payload))
        claims = Claims(
            str(raw["sid"]),
            str(raw["sub"]),
            Purpose(raw["pur"]),
            Audience(raw["aud"]),
            int(raw["exp"]),
            str(raw["jti"]),
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise TokenError("conteúdo inválido") from exc
    if claims.aud is not aud or claims.pur is not purpose:
        raise TokenError("audiência ou finalidade incorreta")
    if int(now.timestamp()) >= claims.exp:
        raise TokenError("token vencido")
    return claims
