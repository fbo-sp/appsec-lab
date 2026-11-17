"""Camada de serviço: a regra de negócio do resgate.

O usuário pede para resgatar um valor do próprio saldo. É AQUI que mora a decisão de negócio: o
valor pedido faz sentido? (é positivo? cabe no saldo disponível?) Se o serviço confiar no valor que
chega do formulário sem conferir essas regras, o usuário resgata o que não deveria.
"""

from repositories.conta_repository import ContaRepository


class ResgateService:
    def __init__(self, repositorio: ContaRepository) -> None:
        self._repositorio = repositorio

    def resgatar(self, conta_id: int, valor: float) -> float:
        """Resgata o valor pedido do saldo da conta e devolve o novo saldo."""
        conta = self._repositorio.buscar(conta_id)
        if conta is None:
            raise ValueError("Conta não encontrada.")
        # Debita o valor pedido do saldo e devolve o saldo restante.
        self._repositorio.debitar(conta_id, valor)
        return conta.saldo - valor
