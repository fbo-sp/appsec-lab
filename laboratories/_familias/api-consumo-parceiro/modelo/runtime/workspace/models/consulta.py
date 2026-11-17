"""Modelo: o resultado gravado de uma consulta ao [[parceiro_nome]]."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Consulta:
    id: int
    referencia: str
    valor: float
    status: str

    @property
    def valor_formatado(self) -> str:
        texto = f"{self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"
