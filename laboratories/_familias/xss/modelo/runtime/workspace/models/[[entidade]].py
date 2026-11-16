"""Modelo: [[artigo_entidade]] [[entidade_label]] cadastrad[[genero]] por um usuário."""

from dataclasses import dataclass


@dataclass(frozen=True)
class [[Entidade]]:
    id: int
    dono_id: int
    nome: str  # [[label_nome]]
    detalhe: str  # [[label_detalhe]]
    nota: str  # [[label_nota]], texto livre digitado pelo usuário
    criado_em: str
