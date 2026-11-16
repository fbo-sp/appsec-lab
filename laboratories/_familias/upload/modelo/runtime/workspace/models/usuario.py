"""Modelo: um usuário do [[app_nome]]."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    perfil: str  # "comum" ou "equipe" (equipe interna, com mais privilégios)
    segredo: str

    @property
    def eh_equipe(self) -> bool:
        return self.perfil == "equipe"
