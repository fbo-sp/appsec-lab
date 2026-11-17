"""Modelo: a conta de um funcionário que acessa o Diretório Corporativo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
