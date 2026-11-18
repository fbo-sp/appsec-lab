"""Modelo: um item da lista do app (Ordens de serviço), que pertence a UM usuário (o dono)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: int
    dono_id: int
    titulo: str
    detalhe: str
    valor: str
