"""Camada de serviço: regras de negócio dos comprovantes de PIX."""

from models.comprovante import Comprovante
from repositories.comprovante_repository import ComprovanteRepository


class ComprovanteService:
    def __init__(self, repositorio: ComprovanteRepository) -> None:
        self._repositorio = repositorio

    def listar(self, cliente_id: int) -> list[Comprovante]:
        """Comprovantes do cliente logado."""
        return self._repositorio.listar_do_cliente(cliente_id)

    def obter(self, comprovante_id: int, cliente_id: int) -> Comprovante | None:
        """Retorna o comprovante pedido pelo cliente logado, ou ``None`` se não existir."""
        return self._repositorio.buscar_por_id(comprovante_id)
