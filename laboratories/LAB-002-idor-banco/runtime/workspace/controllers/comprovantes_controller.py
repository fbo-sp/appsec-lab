"""Camada de controle: páginas e API de comprovantes de PIX."""

from flask import Blueprint, abort, current_app, render_template, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.comprovante_repository import ComprovanteRepository
from services.comprovante_service import ComprovanteService

comprovantes_bp = Blueprint("comprovantes", __name__)


def _servico(conexao) -> ComprovanteService:
    return ComprovanteService(ComprovanteRepository(conexao))


@comprovantes_bp.get("/comprovantes")
@login_obrigatorio
def listar():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        comprovantes = _servico(conexao).listar(session["cliente_id"])
    return render_template("comprovantes.html", comprovantes=comprovantes)


@comprovantes_bp.get("/comprovantes/<int:comprovante_id>")
@login_obrigatorio
def detalhar(comprovante_id: int):
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        comprovante = _servico(conexao).obter(comprovante_id, session["cliente_id"])
    if comprovante is None:
        abort(404)
    return render_template("comprovante.html", comprovante=comprovante)


@comprovantes_bp.get("/api/comprovantes/<int:comprovante_id>")
@login_obrigatorio
def detalhar_api(comprovante_id: int):
    """Mesma informação em JSON, usada pelo aplicativo do celular."""
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        comprovante = _servico(conexao).obter(comprovante_id, session["cliente_id"])
    if comprovante is None:
        return {"erro": "comprovante não encontrado"}, 404
    return comprovante.para_dicionario()
