"""Modelo: a conta de um usuário do App Aurora Campo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    resumo: str
