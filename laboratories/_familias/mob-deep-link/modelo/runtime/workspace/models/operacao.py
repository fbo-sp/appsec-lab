"""Modelo: uma operação sensível do [[app_nome]] ([[operacao_nome]])."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Operacao:
    id: int
    conta_id: int
    alvo: str
    detalhe: str
    status: str  # "pendente" (aguardando o usuário confirmar) ou "concluida"
    criada_em: float
