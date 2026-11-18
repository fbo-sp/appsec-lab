"""Modelo: o exame cadastrado por um usuário."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Exame:
    id: int
    dono_id: int
    nome: str  # Exame
    detalhe: str  # Unidade
    nota: str  # Observação para a coleta, texto livre digitado pelo usuário
    criado_em: str
