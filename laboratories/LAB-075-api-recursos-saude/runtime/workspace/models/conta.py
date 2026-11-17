"""Modelo: a conta de um cliente do Monte Sereno Paciente."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    papel: str
