"""Modelo: um produto da loja de pontos do [[app_nome]]."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Produto:
    id: int
    nome: str
    custo: int
