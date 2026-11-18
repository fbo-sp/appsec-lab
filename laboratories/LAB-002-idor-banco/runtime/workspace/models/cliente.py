"""Modelo de domínio: um cliente do banco."""

from dataclasses import dataclass


@dataclass
class Cliente:
    id: int
    nome: str
    documento: str  # CPF ou CNPJ, já mascarado
    agencia: str
    conta: str
    email: str
