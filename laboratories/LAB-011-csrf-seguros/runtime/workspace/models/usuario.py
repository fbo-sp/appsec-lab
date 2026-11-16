"""Modelo: um usuário do Portal do Segurado."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    chave_pix: str  # chave PIX que recebe as indenizações
