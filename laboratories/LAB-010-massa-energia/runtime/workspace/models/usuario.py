"""Modelo: um usuário do Portal de Fornecedores."""

from dataclasses import asdict, dataclass

PERFIL_COMUM = "fornecedor"
PERFIL_PRIVILEGIADO = "comprador"  # comprador, que aprova pedidos


@dataclass(frozen=True)
class Usuario:
    id: int
    login: str
    nome: str
    email: str
    telefone: str
    perfil: str  # "fornecedor" ou "comprador"
    categoria: str  # categoria do fornecedor, que define alçada e prazo de pagamento

    @property
    def eh_privilegiado(self) -> bool:
        return self.perfil == PERFIL_PRIVILEGIADO

    def como_dict(self) -> dict:
        """Dados que a API devolve (nunca o hash da senha)."""
        return asdict(self)
