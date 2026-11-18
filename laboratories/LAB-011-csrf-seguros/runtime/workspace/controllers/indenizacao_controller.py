"""Camada de controle: tela Conta para indenização."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.historico_repository import HistoricoRepository
from repositories.usuario_repository import UsuarioRepository
from services.indenizacao_service import IndenizacaoService

indenizacao_bp = Blueprint("indenizacao", __name__)


def _servico(conexao) -> IndenizacaoService:
    return IndenizacaoService(UsuarioRepository(conexao), HistoricoRepository(conexao))


@indenizacao_bp.get("/conta-indenizacao")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        dados, historico = _servico(conexao).obter(session["usuario_id"])
    return render_template("indenizacao.html", dados=dados, historico=historico)


@indenizacao_bp.post("/conta-indenizacao")
@login_obrigatorio
def alterar():
    # O usuário já está logado (cookie de sessão), então a alteração é aceita.
    try:
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            _servico(conexao).alterar(
                session["usuario_id"],
                request.form.get("chave_pix", ""),
                request.headers.get("Sec-Fetch-Site", "ausente"),
            )
        flash("Chave PIX de indenização atualizada.")
    except ValueError as erro:
        flash(str(erro))
    return redirect(url_for("indenizacao.ver"))
