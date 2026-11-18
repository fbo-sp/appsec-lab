"""Modelo: a conta de um funcionário que acessa o Diretório de Profissionais."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
