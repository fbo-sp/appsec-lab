"""Camada de serviço: monta o documento para impressão ([[documento_nome]]).

Quem abre o modelo e preenche os campos é a biblioteca ``relatorix`` (veja requirements.txt). Este
serviço só junta os dados da conta e escapa o HTML de cada campo. A falha deste laboratório NÃO
está aqui: está na versão da biblioteca que a aplicação usa.
"""

import html
import os

import relatorix

from models.conta import Conta

# Pasta dos modelos HTML (no contêiner, /workspace/modelos).
PASTA_MODELOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelos")


class DocumentoService:
    def __init__(self, pasta_modelos: str = PASTA_MODELOS) -> None:
        self._gerador = relatorix.Gerador(pasta_modelos)

    def gerar(self, modelo: str, conta: Conta, itens: list[tuple[str, str, str]]) -> str:
        """Preenche o modelo escolhido com os dados da conta e devolve o HTML do documento."""
        linhas = "".join(
            f"<tr><td>{html.escape(data)}</td><td>{html.escape(descricao)}</td><td>{html.escape(valor)}</td></tr>"
            for data, descricao, valor in itens
        )
        dados = {
            "titulo_doc": "[[documento_nome]]",
            "titular": html.escape(conta.nome),
            "login": html.escape(conta.login),
            "linhas": linhas,
        }
        return self._gerador.gerar(modelo, dados)
