"""Camada de serviço: a listagem paginada de atendimentos. É AQUI que mora a falha.

A API recebe ``limite`` (quantos itens por página) do cliente. O app oficial pede 20. O acordo com o
time de infraestrutura é nunca passar de LIMITE_MAXIMO itens por chamada. A falha: o serviço usa o
limite que o cliente mandar, sem teto. Quem pede ``limite=100000`` faz o servidor ler e montar a
base inteira numa resposta só; repetido algumas vezes, derruba o serviço para todos. Detalhe do
SQLite: ``LIMIT -1`` significa "sem limite", então um número negativo também abre tudo. É a falha
"consumo irrestrito de recursos" (OWASP API4).
"""

from models.atendimento import Atendimento
from repositories.atendimento_repository import AtendimentoRepository

LIMITE_MAXIMO = 100  # teto combinado com a infraestrutura (ainda não aplicado)


class AtendimentoService:
    def __init__(self, repositorio: AtendimentoRepository) -> None:
        self._repositorio = repositorio

    def listar(self, conta_id: int, limite: int, pagina: int) -> list[Atendimento]:
        """Devolve uma página de atendimentos da conta, do tamanho que o cliente pedir."""
        deslocamento = max(pagina - 1, 0) * limite
        return self._repositorio.listar(conta_id, limite, deslocamento)
