"""Modelo: um produto da loja de pontos do Clube de Vantagens."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Produto:
    id: int
    nome: str
    custo: int
