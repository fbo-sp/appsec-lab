"""Camada de controle: a área logada do [[app_nome]] e a API de relatório."""

from flask import Blueprint, current_app, jsonify, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from services.erro_service import ErroService
from services.relatorio_service import RelatorioService

painel_bp = Blueprint("painel", __name__)


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
    return render_template("painel.html", conta=conta)


@painel_bp.get("/api/relatorio")
@login_obrigatorio
def relatorio():
    """Gera o relatório do mês informado em ?mes=. Em caso de erro, responde pela ErroService."""
    mes = request.args.get("mes", "")
    try:
        numero = RelatorioService().gerar(mes)
    except Exception as exc:  # noqa: BLE001 - o tratamento de erro é o foco do laboratório
        return jsonify(ErroService().resposta(exc)), 500
    return jsonify({"mes": numero, "status": "ok"})
