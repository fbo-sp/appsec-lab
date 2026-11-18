"""Modelo: a conta de um cliente do Bom Pastor Alertas Clínicos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    papel: str
