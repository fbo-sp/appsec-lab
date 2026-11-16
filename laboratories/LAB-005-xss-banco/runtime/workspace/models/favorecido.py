"""Modelo: o favorecido cadastrado por um usuário."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Favorecido:
    id: int
    dono_id: int
    nome: str  # Nome do favorecido
    detalhe: str  # Chave PIX
    nota: str  # Apelido, texto livre digitado pelo usuário
    criado_em: str
