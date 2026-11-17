"""Modelo: um [[recurso_singular]] de uma conta do [[app_nome]]."""

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
