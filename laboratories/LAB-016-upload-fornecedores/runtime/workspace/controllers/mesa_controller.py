"""Camada de controle: Conferência de compras, só para a equipe (compradores)."""

from flask import Blueprint, current_app, render_template

from controllers.auth_controller import equipe_obrigatoria
from database.conexao import abrir_conexao
from repositories.anexo_repository import AnexoRepository

mesa_bp = Blueprint("mesa", __name__)


@mesa_bp.get("/mesa")
@equipe_obrigatoria
def listar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        anexos = AnexoRepository(conexao).listar_todos()
    return render_template("mesa.html", anexos=anexos)
