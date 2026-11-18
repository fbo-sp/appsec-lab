"""Inspeção do banco da cópia avaliada (ADR-023), somente stdlib. Roda em contêiner efêmero SEM rede.

Lê ``/probe/inspect.json`` = {"files": {"<db_path>": "/probe/db/0.sqlite"}, "inspections": [...]} e
imprime ``{"results": {"<id>": true|false}}``. O arquivo do banco veio da cópia isolada (dado não
confiável): é aberto só para leitura e qualquer erro de leitura reprova a inspeção (fail closed).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import sqlite3
import sys
from typing import Any


def verify_werkzeug_hash(stored: str, password: str) -> bool:
    """Confere um hash no formato do Werkzeug (``scrypt:`` ou ``pbkdf2:``), sem depender dele."""
    try:
        method, salt, hexhash = stored.split("$", 2)
        parts = method.split(":")
        if parts[0] == "scrypt":
            n, r, p = (int(x) for x in parts[1:4])
            if n > 2**17 or r > 16 or p > 4:
                return False
            dk = hashlib.scrypt(
                password.encode(), salt=salt.encode(), n=n, r=r, p=p, maxmem=132 * n * r * p
            ).hex()
        elif parts[0] == "pbkdf2":
            algo, iterations = parts[1], int(parts[2])
            if algo not in ("sha256", "sha512") or not 1 <= iterations <= 2_000_000:
                return False
            dk = hashlib.pbkdf2_hmac(algo, password.encode(), salt.encode(), iterations).hex()
        else:
            return False
    except (ValueError, IndexError, OverflowError, MemoryError):
        return False
    return hmac.compare_digest(dk, hexhash)


def _check(item: dict[str, Any], db_file: str | None) -> bool:
    if db_file is None:
        return False
    try:
        con = sqlite3.connect(f"file:{db_file}?mode=ro&immutable=1", uri=True)
        try:
            rows = con.execute(str(item["query"])).fetchmany(1000)
        finally:
            con.close()
    except sqlite3.Error:
        return False
    pairs = [(str(r[0]), "" if r[1] is None else str(r[1])) for r in rows if len(r) >= 2]
    if len(pairs) < int(item.get("min_rows", 1)):
        return False
    if item.get("all_match") and not all(re.fullmatch(item["all_match"], v) for _, v in pairs):
        return False
    if item.get("none_match") and any(re.search(item["none_match"], v) for _, v in pairs):
        return False
    wanted = item.get("verify_passwords") or {}
    found = dict(pairs)
    return all(k in found and verify_werkzeug_hash(found[k], pw) for k, pw in wanted.items())


def run(spec: dict[str, Any]) -> dict[str, bool]:
    files = spec.get("files", {})
    return {str(i["id"]): _check(i, files.get(i["db_path"])) for i in spec.get("inspections", [])}


if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else "/probe/inspect.json", encoding="utf-8") as fh:
        print(json.dumps({"results": run(json.load(fh))}))
