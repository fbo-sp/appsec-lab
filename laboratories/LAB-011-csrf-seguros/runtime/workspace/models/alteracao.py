"""Modelo: uma alteração registrada no histórico de chave PIX de indenização."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Alteracao:
    quando: str
    valor_anterior: str
    valor_novo: str
