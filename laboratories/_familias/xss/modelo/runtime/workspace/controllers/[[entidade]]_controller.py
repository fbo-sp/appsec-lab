"""Camada de controle: [[rotulo_busca_minusculo]] e cadastro de [[entidades_label]]."""

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.[[entidade]]_repository import [[Entidade]]Repository
from services.[[entidade]]_service import [[Entidade]]Service

[[entidade]]_bp = Blueprint("[[entidade]]", __name__)


@[[entidade]]_bp.get("/[[rota]]")
@login_obrigatorio
def buscar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = [[Entidade]]Service([[Entidade]]Repository(conexao))
        termo, itens = servico.buscar(session["usuario_id"], request.args.get("q", ""))
    return render_template("[[rota]].html", termo=termo, itens=itens, erro=request.args.get("erro"))


@[[entidade]]_bp.post("/[[rota]]/novo")
@login_obrigatorio
def cadastrar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = [[Entidade]]Service([[Entidade]]Repository(conexao))
        try:
            servico.cadastrar(
                session["usuario_id"],
                request.form.get("nome", ""),
                request.form.get("detalhe", ""),
                request.form.get("nota", ""),
            )
        except ValueError as exc:
            return redirect(url_for("[[entidade]].buscar", erro=str(exc)))
    return redirect(url_for("[[entidade]].buscar"))
