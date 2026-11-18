"""Modelo: uma alteração registrada no histórico de e-mail para envio de laudos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Alteracao:
    quando: str
    valor_anterior: str
    valor_novo: str
