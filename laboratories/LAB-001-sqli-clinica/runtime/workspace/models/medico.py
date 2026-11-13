"""Modelo de domínio: um médico do corpo clínico."""

from dataclasses import dataclass


@dataclass
class Medico:
    id: int
    nome: str
    especialidade: str
    crm: str
