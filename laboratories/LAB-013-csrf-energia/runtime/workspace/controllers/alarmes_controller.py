"""Camada de controle: tela Plantão de alarmes."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.historico_repository import HistoricoRepository
from repositories.usuario_repository import UsuarioRepository
from services.alarmes_service import AlarmesService

alarmes_bp = Blueprint("alarmes", __name__)


def _servico(conexao) -> AlarmesService:
    return AlarmesService(UsuarioRepository(conexao), HistoricoRepository(conexao))


@alarmes_bp.get("/alarmes/plantao")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        dados, historico = _servico(conexao).obter(session["usuario_id"])
    return render_template("alarmes.html", dados=dados, historico=historico)


@alarmes_bp.post("/alarmes/plantao")
@login_obrigatorio
def alterar():
    # O usuário já está logado (cookie de sessão), então a alteração é aceita.
    try:
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            _servico(conexao).alterar(
                session["usuario_id"],
                request.form.get("celular_plantao", ""),
                request.headers.get("Sec-Fetch-Site", "ausente"),
            )
        flash("Celular do plantão atualizado.")
    except ValueError as erro:
        flash(str(erro))
    return redirect(url_for("alarmes.ver"))
