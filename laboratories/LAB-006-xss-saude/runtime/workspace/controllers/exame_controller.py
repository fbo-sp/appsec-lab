"""Camada de controle: busca de exames e cadastro de exames."""

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.exame_repository import ExameRepository
from services.exame_service import ExameService

exame_bp = Blueprint("exame", __name__)


@exame_bp.get("/exames")
@login_obrigatorio
def buscar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = ExameService(ExameRepository(conexao))
        termo, itens = servico.buscar(session["usuario_id"], request.args.get("q", ""))
    return render_template("exames.html", termo=termo, itens=itens, erro=request.args.get("erro"))


@exame_bp.post("/exames/novo")
@login_obrigatorio
def cadastrar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = ExameService(ExameRepository(conexao))
        try:
            servico.cadastrar(
                session["usuario_id"],
                request.form.get("nome", ""),
                request.form.get("detalhe", ""),
                request.form.get("nota", ""),
            )
        except ValueError as exc:
            return redirect(url_for("exame.buscar", erro=str(exc)))
    return redirect(url_for("exame.buscar"))
