"""Camada de controle: a área logada do Portal do Cliente e o pedido de resgate."""

from flask import Blueprint, current_app, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from services.resgate_service import ResgateService

painel_bp = Blueprint("painel", __name__)


def _mostrar(conexao, resultado=None, erro=None):
    conta = ContaRepository(conexao).buscar(session["usuario_id"])
    return render_template("painel.html", conta=conta, resultado=resultado, erro=erro)


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        return _mostrar(conexao)


@painel_bp.post("/resgatar")
@login_obrigatorio
def resgatar():
    bruto = request.form.get("valor", "")
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        try:
            valor = float(bruto.replace(",", "."))
        except ValueError:
            return _mostrar(conexao, erro="Informe um valor numérico.")
        try:
            novo = ResgateService(ContaRepository(conexao)).resgatar(session["usuario_id"], valor)
        except ValueError as erro:
            return _mostrar(conexao, erro=str(erro))
        return _mostrar(conexao, resultado=f"Operação registrada. Saldo disponível: R$ {novo:.2f}.")
