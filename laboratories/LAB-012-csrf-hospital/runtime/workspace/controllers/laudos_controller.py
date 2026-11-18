"""Camada de controle: tela Envio de laudos."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.historico_repository import HistoricoRepository
from repositories.usuario_repository import UsuarioRepository
from services.laudos_service import LaudosService

laudos_bp = Blueprint("laudos", __name__)


def _servico(conexao) -> LaudosService:
    return LaudosService(UsuarioRepository(conexao), HistoricoRepository(conexao))


@laudos_bp.get("/laudos/envio")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        dados, historico = _servico(conexao).obter(session["usuario_id"])
    return render_template("laudos.html", dados=dados, historico=historico)


@laudos_bp.post("/laudos/envio")
@login_obrigatorio
def alterar():
    # O usuário já está logado (cookie de sessão), então a alteração é aceita.
    try:
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            _servico(conexao).alterar(
                session["usuario_id"],
                request.form.get("email_laudos", ""),
                request.headers.get("Sec-Fetch-Site", "ausente"),
            )
        flash("E-mail para envio de laudos atualizado.")
    except ValueError as erro:
        flash(str(erro))
    return redirect(url_for("laudos.ver"))
