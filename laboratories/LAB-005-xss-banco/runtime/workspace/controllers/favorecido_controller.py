"""Camada de controle: busca de favorecidos e cadastro de favorecidos."""

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.favorecido_repository import FavorecidoRepository
from services.favorecido_service import FavorecidoService

favorecido_bp = Blueprint("favorecido", __name__)


@favorecido_bp.get("/favorecidos")
@login_obrigatorio
def buscar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = FavorecidoService(FavorecidoRepository(conexao))
        termo, itens = servico.buscar(session["usuario_id"], request.args.get("q", ""))
    return render_template("favorecidos.html", termo=termo, itens=itens, erro=request.args.get("erro"))


@favorecido_bp.post("/favorecidos/novo")
@login_obrigatorio
def cadastrar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = FavorecidoService(FavorecidoRepository(conexao))
        try:
            servico.cadastrar(
                session["usuario_id"],
                request.form.get("nome", ""),
                request.form.get("detalhe", ""),
                request.form.get("nota", ""),
            )
        except ValueError as exc:
            return redirect(url_for("favorecido.buscar", erro=str(exc)))
    return redirect(url_for("favorecido.buscar"))
