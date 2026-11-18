"""Modelo: um usuário do Portal de Agendamento."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    perfil: str  # "comum" ou "equipe" (equipe interna, que vê os anexos de todos)

    @property
    def eh_equipe(self) -> bool:
        return self.perfil == "equipe"
