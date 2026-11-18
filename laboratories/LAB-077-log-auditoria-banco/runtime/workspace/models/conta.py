"""Modelo: a conta de um cliente do Portal do Corretor Maré Alta."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    papel: str
