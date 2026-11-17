"""Camada de serviço: a resolução de um pedido na API GraphQL. É AQUI que mora a falha.

O resolver recebe o id do usuário logado e o id do pedido pedido na query. A falha: ele devolve o
pedido só pelo id, SEM conferir se aquele pedido pertence ao usuário logado. Então, logado como um
usuário, dá para pedir o pedido de QUALQUER outro só trocando o id — é BOLA (Broken Object Level
Authorization), a autorização por objeto quebrada. A defesa é conferir, no resolver, que o objeto
pedido é do dono que está logado antes de devolvê-lo.
"""

from models.pedido import Pedido
from repositories.pedido_repository import PedidoRepository


class PedidoService:
    def __init__(self, repositorio: PedidoRepository) -> None:
        self._repositorio = repositorio

    def resolver(self, usuario_id: int, pedido_id: int) -> Pedido | None:
        """Resolve o pedido pedido na query GraphQL para o usuário logado."""
        # Devolve o pedido só pelo id, sem conferir se o dono é o usuário logado.
        return self._repositorio.buscar(pedido_id)
