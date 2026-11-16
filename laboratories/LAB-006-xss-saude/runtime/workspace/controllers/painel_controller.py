"""Camada de controle: fila de atendimento, usado pela equipe interna."""

from flask import Blueprint, current_app, render_template

from controllers.auth_controller import equipe_obrigatoria
from database.conexao import abrir_conexao
from repositories.exame_repository import ExameRepository
from services.exame_service import ExameService

painel_bp = Blueprint("painel", __name__)


@painel_bp.get("/painel")
@equipe_obrigatoria
def listar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        recentes = ExameService(ExameRepository(conexao)).recentes()
    return render_template("painel.html", recentes=recentes)
