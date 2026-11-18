"""Camada de controle: busca de ordens de serviço e cadastro de ordens de serviço."""

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.ordem_repository import OrdemRepository
from services.ordem_service import OrdemService

ordem_bp = Blueprint("ordem", __name__)


@ordem_bp.get("/ordens")
@login_obrigatorio
def buscar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = OrdemService(OrdemRepository(conexao))
        termo, itens = servico.buscar(session["usuario_id"], request.args.get("q", ""))
    return render_template("ordens.html", termo=termo, itens=itens, erro=request.args.get("erro"))


@ordem_bp.post("/ordens/novo")
@login_obrigatorio
def cadastrar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = OrdemService(OrdemRepository(conexao))
        try:
            servico.cadastrar(
                session["usuario_id"],
                request.form.get("nome", ""),
                request.form.get("detalhe", ""),
                request.form.get("nota", ""),
            )
        except ValueError as exc:
            return redirect(url_for("ordem.buscar", erro=str(exc)))
    return redirect(url_for("ordem.buscar"))
