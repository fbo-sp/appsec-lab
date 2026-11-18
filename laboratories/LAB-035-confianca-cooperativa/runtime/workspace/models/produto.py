"""Modelo: um produto da loja de pontos do Clube de Pontos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Produto:
    id: int
    nome: str
    custo: int
