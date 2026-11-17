"""Camada de serviço: o perfil mostrado na tela Perfil do app. É AQUI que mora a falha.

A tela Perfil mostra só o nome e o resumo. A falha: o serviço devolve o registro inteiro da conta, com
documento e dado pessoal. Tudo o que a API devolve chega ao aparelho, mesmo que a tela não mostre.
"""

from repositories.conta_repository import ContaRepository


class PerfilService:
    def __init__(self, repositorio: ContaRepository) -> None:
        self._repositorio = repositorio

    def perfil(self, conta_id: int) -> dict[str, str]:
        """Os dados do perfil que a API entrega ao app."""
        # Devolve o registro inteiro da conta; a tela do app só mostra nome e resumo.
        return self._repositorio.perfil_completo(conta_id)
