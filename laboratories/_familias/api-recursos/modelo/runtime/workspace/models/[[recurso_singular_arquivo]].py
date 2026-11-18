"""Modelo: um [[recurso_singular]] da conta."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class [[classe]]:
    id: int
    data: str
    descricao: str
    valor: float

    def como_dict(self) -> dict[str, object]:
        return asdict(self)
