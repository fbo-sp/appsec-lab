"""Modelo de domínio: um CLP (controlador lógico programável) da planta."""

from dataclasses import dataclass


@dataclass
class Equipamento:
    endereco: str
    nome: str
    linha: str
