"""Camada de controle: a área logada do Nébula Cartões Online."""

from flask import Blueprint, current_app, render_template, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.item_repository import ItemRepository

painel_bp = Blueprint("painel", __name__)


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
        itens = ItemRepository(conexao).da_conta(session["usuario_id"])
    return render_template("painel.html", conta=conta, itens=itens)
