"""Camada de controle: [[painel_titulo_minusculo]], usado pela equipe interna."""

from flask import Blueprint, current_app, render_template

from controllers.auth_controller import equipe_obrigatoria
from database.conexao import abrir_conexao
from repositories.[[entidade]]_repository import [[Entidade]]Repository
from services.[[entidade]]_service import [[Entidade]]Service

painel_bp = Blueprint("painel", __name__)


@painel_bp.get("/painel")
@equipe_obrigatoria
def listar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        recentes = [[Entidade]]Service([[Entidade]]Repository(conexao)).recentes()
    return render_template("painel.html", recentes=recentes)
