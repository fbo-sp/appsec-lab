"""Modelo: um usuário do [[app_nome]]."""

from dataclasses import asdict, dataclass

PERFIL_COMUM = "[[perfil_comum]]"
PERFIL_PRIVILEGIADO = "[[perfil_priv]]"  # [[perfil_priv_desc]]


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    email: str
    telefone: str
    perfil: str  # "[[perfil_comum]]" ou "[[perfil_priv]]"
    [[campo]]: str  # [[campo_desc]]

    @property
    def eh_privilegiado(self) -> bool:
        return self.perfil == PERFIL_PRIVILEGIADO

    def como_dict(self) -> dict:
        """Dados que a API devolve (nunca o hash da senha)."""
        return asdict(self)
