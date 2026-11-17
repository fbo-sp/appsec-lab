"""Modelo: a conta de um usuário do Portal do Investidor."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    saldo: float
