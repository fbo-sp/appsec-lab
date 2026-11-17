"""Modelo: a conta de um usuário do Console Interno, com o papel (comum ou admin)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    papel: str
