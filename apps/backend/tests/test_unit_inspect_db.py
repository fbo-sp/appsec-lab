"""Inspeção do banco da cópia avaliada (ADR-023): regras de valor e conferência de hash do Werkzeug."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest
from app.validation import inspect_db
from app.validation.suites import InspectCheck


def _scrypt(pw: str, salt: str = "abc123", n: int = 16384) -> str:
    dk = hashlib.scrypt(pw.encode(), salt=salt.encode(), n=n, r=8, p=1, maxmem=132 * n * 8).hex()
    return f"scrypt:{n}:8:1${salt}${dk}"


def _pbkdf2(pw: str, salt: str = "s4lt", it: int = 1000) -> str:
    return f"pbkdf2:sha256:{it}${salt}$" + hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), it).hex()


def _db(tmp_path: Path, rows: list[tuple[str, str]]) -> str:
    path = tmp_path / "app.db"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE usuarios (login TEXT, senha_hash TEXT)")
    con.executemany("INSERT INTO usuarios VALUES (?, ?)", rows)
    con.commit()
    con.close()
    return str(path)


def _check(**over: object) -> dict[str, object]:
    base = InspectCheck(
        id="hash-forte",
        description="d",
        db_path="/tmp/app.db",
        query="SELECT login, senha_hash FROM usuarios",
        all_match=r"(scrypt|pbkdf2):.+",
        none_match=r"^[0-9a-f]{32}$",
        verify_passwords={"ana": "Senha-Ana-1"},
    ).to_probe()
    base.update(over)
    return base


def test_werkzeug_formats_verify_and_reject_wrong_password() -> None:
    assert inspect_db.verify_werkzeug_hash(_scrypt("x"), "x")
    assert inspect_db.verify_werkzeug_hash(_pbkdf2("x"), "x")
    assert not inspect_db.verify_werkzeug_hash(_scrypt("x"), "y")
    assert not inspect_db.verify_werkzeug_hash(hashlib.md5(b"x").hexdigest(), "x")
    assert not inspect_db.verify_werkzeug_hash("scrypt:999999999:8:1$s$00", "x")  # custo absurdo: recusa


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        ([("ana", _scrypt("Senha-Ana-1")), ("bia", _pbkdf2("outra"))], True),
        ([("ana", _scrypt("Senha-Ana-1")), ("bia", hashlib.md5(b"b").hexdigest())], False),
        ([("ana", "Senha-Ana-1")], False),  # texto puro
        ([("ana", "scrypt:16384:8:1$abc$" + "0" * 128)], False),  # prefixo forte, hash falso
        ([], False),
    ],
)
def test_inspection_rules(tmp_path: Path, rows: list[tuple[str, str]], expected: bool) -> None:
    spec = {"files": {"/tmp/app.db": _db(tmp_path, rows)}, "inspections": [_check()]}
    assert inspect_db.run(spec) == {"hash-forte": expected}


def test_missing_or_corrupt_file_fails_closed(tmp_path: Path) -> None:
    bad = tmp_path / "x.db"
    bad.write_bytes(b"isto nao e sqlite")
    assert inspect_db.run({"files": {}, "inspections": [_check()]}) == {"hash-forte": False}
    spec = {"files": {"/tmp/app.db": str(bad)}, "inspections": [_check()]}
    assert inspect_db.run(spec) == {"hash-forte": False}
