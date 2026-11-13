"""Camada de serviço: regras de negócio da busca de médicos."""

from models.medico import Medico
from repositories.medico_repository import MedicoRepository


class MedicoService:
    def __init__(self, repositorio: MedicoRepository, tamanho_maximo: int) -> None:
        self._repositorio = repositorio
        self._tamanho_maximo = tamanho_maximo

    def buscar(self, termo: str) -> list[Medico]:
        """Normaliza o termo digitado e delega a consulta ao repositório."""
        termo = termo.strip()[: self._tamanho_maximo]
        return self._repositorio.buscar_por_nome(termo)
