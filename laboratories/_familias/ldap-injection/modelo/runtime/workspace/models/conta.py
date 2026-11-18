"""Modelo: a conta de um funcionário que acessa o [[app_nome]]."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
