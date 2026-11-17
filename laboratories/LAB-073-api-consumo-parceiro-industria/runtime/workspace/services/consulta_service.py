"""Camada de serviço: grava o resultado da consulta ao Rolamax. É AQUI que mora a falha.

O contrato combinado com o parceiro diz que a resposta tem exatamente dois campos: ``referencia`` e
``preco_unitario`` (número entre 0 e R$ 10.000). A falha: este serviço grava o que vier, como veio. Se o
parceiro for invadido ou tiver um defeito, valores absurdos entram no nosso banco e um campo que nem
existe no contrato (``aprovacao_automatica``) decide o status. Confiar sem conferir a API de um
terceiro é a falha "consumo inseguro de APIs" (OWASP API10).
"""

from models.consulta import Consulta
from repositories.consulta_repository import ConsultaRepository


class RespostaInvalida(Exception):
    """A resposta do parceiro não segue o contrato combinado."""


class ConsultaService:
    def __init__(self, repositorio: ConsultaRepository) -> None:
        self._repositorio = repositorio

    def registrar(self, conta_id: int, referencia: str, dados: dict) -> Consulta:
        """Grava a resposta do parceiro como veio."""
        valor = dados["preco_unitario"]
        status = "aprovado" if dados.get("aprovacao_automatica") else "em análise"
        return self._repositorio.inserir(conta_id, referencia, valor, status)
