"""Modelo: um pedido/registro que pertence a UM usuário (o dono)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pedido:
    id: int
    dono_id: int
    descricao: str
    valor: float
