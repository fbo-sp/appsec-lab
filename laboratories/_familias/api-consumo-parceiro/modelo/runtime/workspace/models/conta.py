"""Modelo: a conta de um cliente do [[app_nome]]."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    papel: str
