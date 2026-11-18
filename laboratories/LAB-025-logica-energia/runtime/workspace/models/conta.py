"""Modelo: a conta de um usuário do Portal do Cliente, com o saldo que ele pode resgatar."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    saldo: float
