"""Camada de controle: tela [[tela_titulo]]."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.historico_repository import HistoricoRepository
from repositories.usuario_repository import UsuarioRepository
from services.[[modulo]]_service import [[Modulo]]Service

[[modulo]]_bp = Blueprint("[[modulo]]", __name__)


def _servico(conexao) -> [[Modulo]]Service:
    return [[Modulo]]Service(UsuarioRepository(conexao), HistoricoRepository(conexao))


@[[modulo]]_bp.get("/[[rota]]")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        dados, historico = _servico(conexao).obter(session["usuario_id"])
    return render_template("[[modulo]].html", dados=dados, historico=historico)


@[[modulo]]_bp.post("/[[rota]]")
@login_obrigatorio
def alterar():
    # O usuário já está logado (cookie de sessão), então a alteração é aceita.
    try:
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            _servico(conexao).alterar(
                session["usuario_id"],
                request.form.get("[[campo]]", ""),
                request.headers.get("Sec-Fetch-Site", "ausente"),
            )
        flash("[[msg_sucesso]]")
    except ValueError as erro:
        flash(str(erro))
    return redirect(url_for("[[modulo]].ver"))
