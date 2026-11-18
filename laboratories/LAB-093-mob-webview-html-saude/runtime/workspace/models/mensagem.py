"""Modelo: uma mensagem da central de mensagens do App Lumen Saúde (Convites e recados)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Mensagem:
    id: int
    autor: str
    texto: str
    enviada_em: str
