"""Camada de controle: a área logada do [[app_nome]] e a API de perfil (com CORS)."""

from flask import Blueprint, current_app, jsonify, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from services.cors_service import CorsService

painel_bp = Blueprint("painel", __name__)


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
    return render_template("painel.html", conta=conta)


@painel_bp.get("/api/perfil")
@login_obrigatorio
def perfil():
    """Devolve, em JSON, o perfil do usuário logado — consumido pela própria página via fetch()."""
    origem = request.headers.get("Origin", "")
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
    resposta = jsonify({"nome": conta.nome, "login": conta.login})
    for nome, valor in CorsService().cabecalhos(origem).items():
        resposta.headers[nome] = valor
    return resposta
