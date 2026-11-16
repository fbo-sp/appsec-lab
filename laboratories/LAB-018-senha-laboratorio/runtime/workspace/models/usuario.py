"""Modelo: um usuário do Portal do Paciente."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
