"""Modelo: um usuário do App Trilha Pay."""

from dataclasses import asdict, dataclass

PERFIL_COMUM = "cliente"
PERFIL_PRIVILEGIADO = "analista"  # analista de crédito, que aprova aumentos de limite


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    email: str
    telefone: str
    perfil: str  # "cliente" ou "analista"
    pacote: str  # pacote contratado, que define limites e tarifas

    @property
    def eh_privilegiado(self) -> bool:
        return self.perfil == PERFIL_PRIVILEGIADO

    def como_dict(self) -> dict:
        """Dados que a API devolve (nunca o hash da senha)."""
        return asdict(self)
