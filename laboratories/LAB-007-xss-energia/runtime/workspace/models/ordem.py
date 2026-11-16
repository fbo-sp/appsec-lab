"""Modelo: a ordem de serviço cadastrada por um usuário."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Ordem:
    id: int
    dono_id: int
    nome: str  # Equipamento
    detalhe: str  # Subestação
    nota: str  # Relato do técnico, texto livre digitado pelo usuário
    criado_em: str
