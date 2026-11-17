"""Modelo: a conta de um cliente do Ventura Operação."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    papel: str
