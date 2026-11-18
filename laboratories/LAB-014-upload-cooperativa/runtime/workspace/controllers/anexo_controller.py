"""Camada de controle: envio de comprovantes de renda e download dos anexos."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, session, url_for

from config import Config
from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.anexo_repository import AnexoRepository
from services.anexo_service import AnexoService

anexo_bp = Blueprint("anexo", __name__)


@anexo_bp.route("/comprovantes", methods=["GET", "POST"])
@login_obrigatorio
def enviar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        repositorio = AnexoRepository(conexao)
        if request.method == "POST":
            try:
                nome = AnexoService(repositorio).salvar(
                    session["usuario_id"], request.form.get("descricao", ""), request.files.get("arquivo")
                )
                flash(f"Comprovante recebido para análise. Arquivo: {nome}")
                return redirect(url_for("anexo.enviar"))
            except ValueError as erro:
                anexos = repositorio.listar_do_dono(session["usuario_id"])
                return render_template("envio.html", anexos=anexos, erro=str(erro)), 400
        anexos = repositorio.listar_do_dono(session["usuario_id"])
    return render_template("envio.html", anexos=anexos, erro=None)


@anexo_bp.get("/anexos/<nome>")
@login_obrigatorio
def baixar(nome: str):
    """Mostra o arquivo no navegador. O Content-Type vem da extensão do nome."""
    return send_from_directory(Config.PASTA_ANEXOS, nome)
