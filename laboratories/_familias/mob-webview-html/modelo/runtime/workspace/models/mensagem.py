"""Modelo: uma mensagem da central de mensagens do [[app_nome]] ([[mensagens_titulo]])."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Mensagem:
    id: int
    autor: str
    texto: str
    enviada_em: str
