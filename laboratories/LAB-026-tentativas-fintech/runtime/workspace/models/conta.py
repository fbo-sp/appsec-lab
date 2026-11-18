"""Modelo: a conta de um usuário do Área do Cliente."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    saldo: float
