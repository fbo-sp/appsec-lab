"""Modelo: uma mensagem da central de mensagens do App Aurora Campo (Avisos de turno)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Mensagem:
    id: int
    autor: str
    texto: str
    enviada_em: str
