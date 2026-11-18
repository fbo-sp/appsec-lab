"""Modelo: a conta de um usuário do Painel de Relatórios."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conta:
    id: int
    login: str
    nome: str
    saldo: float
