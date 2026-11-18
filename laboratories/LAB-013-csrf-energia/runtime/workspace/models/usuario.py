"""Modelo: um usuário do Supervisório PCH Rio Claro."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    celular_plantao: str  # celular que recebe os alarmes críticos por SMS
