"""Modelo: um usuário do Acesso Cooperado."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
