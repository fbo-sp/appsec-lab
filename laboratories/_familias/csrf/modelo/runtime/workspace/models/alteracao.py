"""Modelo: uma alteração registrada no histórico de [[campo_label_minusculo]]."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Alteracao:
    quando: str
    valor_anterior: str
    valor_novo: str
