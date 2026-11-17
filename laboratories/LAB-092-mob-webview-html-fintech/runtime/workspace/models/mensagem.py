"""Modelo: uma mensagem da central de mensagens do App Pagomais (Mensagens do Pix)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Mensagem:
    id: int
    autor: str
    texto: str
    enviada_em: str
