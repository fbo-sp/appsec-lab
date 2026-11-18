"""Modelo: a conta de um cliente do Nébula Cartões Online."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    papel: str
