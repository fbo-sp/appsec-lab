"""Modelo: a conta de um usuário do Portal de Exames."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
