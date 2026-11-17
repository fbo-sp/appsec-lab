"""Camada de serviço: libera o recurso do plano avançado (Relatório de ativos). É AQUI que mora a falha.

O app só mostra o botão do recurso para quem é do plano avançado (habilitação de supervisor) e manda, junto com
o pedido, o plano da conta e o resultado da própria verificação de integridade ("ok"). O servidor
confia nesses dois campos. A falha: o app roda no celular do usuário e pode ser modificado
(reempacotado); um app modificado manda o que quiser, e o servidor libera o recurso para qualquer conta.
"""

from repositories.assinatura_repository import AssinaturaRepository
from services.atestacao_service import AtestacaoService


class RecursoService:
    def __init__(self, assinaturas: AssinaturaRepository, atestacao: AtestacaoService) -> None:
        self._assinaturas = assinaturas
        self._atestacao = atestacao

    def liberar(self, conta_id: int, dados: dict) -> bool:
        """Decide se a conta pode usar o recurso do plano avançado."""
        # O app já confere o plano e a própria integridade antes de mostrar o botão: o servidor confia.
        plano = dados.get("plano")
        app_integro = dados.get("integridade") == "ok"
        return app_integro and plano == "avancado"
