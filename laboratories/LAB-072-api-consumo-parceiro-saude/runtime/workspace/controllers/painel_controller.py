"""Camada de controle: a área logada do Bem Cuidar Reembolso e a consulta ao Rede Atlas Credenciados."""

import logging

from flask import Blueprint, current_app, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.consulta_repository import ConsultaRepository
from services.consulta_service import ConsultaService, RespostaInvalida
from services.parceiro_client import ParceiroClient, ParceiroIndisponivel

painel_bp = Blueprint("painel", __name__)
logger = logging.getLogger("consultas")


def _pagina(mensagem: str | None = None, erro: str | None = None, status: int = 200):
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        repositorio = ConsultaRepository(conexao)
        pendencias = repositorio.listar_pendencias(session["usuario_id"])
        consultas = repositorio.listar_consultas(session["usuario_id"])
    return render_template(
        "painel.html", pendencias=pendencias, consultas=consultas, mensagem=mensagem, erro=erro
    ), status


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    return _pagina()


@painel_bp.post("/consultas")
@login_obrigatorio
def consultar():
    """Consulta o parceiro para uma pedido e grava o resultado."""
    referencia = request.form.get("referencia", "")
    try:
        dados = ParceiroClient(current_app.config["URL_PARCEIRO"]).consultar(referencia)
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            consulta = ConsultaService(ConsultaRepository(conexao)).registrar(session["usuario_id"], referencia, dados)
    except ParceiroIndisponivel:
        return _pagina(erro="O Rede Atlas Credenciados não respondeu. Tente de novo.", status=502)
    except RespostaInvalida as motivo:
        logger.warning("Resposta do parceiro recusada: referencia=%s motivo=%s", referencia, motivo)
        return _pagina(erro="Resposta do parceiro inválida: nada foi gravado.", status=502)
    logger.info("Consulta gravada: referencia=%s valor=%s status=%s", referencia, consulta.valor, consulta.status)
    return _pagina(mensagem=f"Consulta {referencia} gravada: Valor de reembolso {consulta.valor_formatado}, status {consulta.status}.")
