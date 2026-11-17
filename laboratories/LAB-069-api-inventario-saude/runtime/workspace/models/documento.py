"""Modelo: um exame de uma conta do Íris Resultados."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Documento:
    id: int
    conta_id: int
    titular: str
    titulo: str
    data: str
    detalhe: str

    def como_dict(self) -> dict[str, object]:
        return asdict(self)
