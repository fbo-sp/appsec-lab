"""Camada de controle: a área logada do Cobalto Online e a documentação publicada da API."""

from flask import Blueprint, current_app, render_template, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.documento_repository import DocumentoRepository

painel_bp = Blueprint("painel", __name__)


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
        documentos = DocumentoRepository(conexao).listar_da_conta(session["usuario_id"])
    return render_template("painel.html", conta=conta, documentos=documentos)


@painel_bp.get("/api/docs")
def documentacao():
    """Documentação pública da API, a que os times de app e os parceiros consultam."""
    return render_template("docs.html")
