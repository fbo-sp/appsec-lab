"""Camada de serviço: o resgate de um produto na loja de pontos. É AQUI que mora a falha.

O usuário resgata um produto gastando pontos do saldo. A pergunta de SEGURANÇA é: quem decide
quanto custa o produto? O custo é um dado da LOJA — ele está no banco, no servidor. Se o serviço
confiar no custo que veio do formulário, o usuário manda o custo que quiser (1 ponto) e leva um
produto caro de graça. É o clássico "confiar num dado que o cliente controla, mas que o servidor
deveria determinar sozinho".
"""

from repositories.conta_repository import ContaRepository
from repositories.produto_repository import ProdutoRepository


class LojaService:
    def __init__(self, contas: ContaRepository, produtos: ProdutoRepository) -> None:
        self._contas = contas
        self._produtos = produtos

    def resgatar(self, conta_id: int, produto_id: int, custo_informado: int) -> float:
        """Resgata o produto para a conta e devolve o novo saldo de pontos."""
        conta = self._contas.buscar(conta_id)
        if conta is None:
            raise ValueError("Conta não encontrada.")
        produto = self._produtos.buscar(produto_id)
        if produto is None:
            raise ValueError("Produto não encontrado.")
        # Usa o custo que veio do formulário, sem conferir com o custo real do produto no banco.
        self._contas.debitar(conta_id, custo_informado)
        return conta.saldo - custo_informado
