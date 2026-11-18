"""Modelo: um usuário do Portal do Beneficiário."""

from dataclasses import asdict, dataclass

PERFIL_COMUM = "beneficiario"
PERFIL_PRIVILEGIADO = "auditor"  # auditoria médica, que libera procedimentos


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    email: str
    telefone: str
    perfil: str  # "beneficiario" ou "auditor"
    plano: str  # plano contratado, que define rede e reembolso

    @property
    def eh_privilegiado(self) -> bool:
        return self.perfil == PERFIL_PRIVILEGIADO

    def como_dict(self) -> dict:
        """Dados que a API devolve (nunca o hash da senha)."""
        return asdict(self)
