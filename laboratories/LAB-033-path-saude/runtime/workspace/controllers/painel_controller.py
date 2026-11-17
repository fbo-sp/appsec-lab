"""Camada de controle: a área logada do Central de Documentos e o download de documentos."""

from flask import Blueprint, Response, current_app, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from services.documento_service import DocumentoService

painel_bp = Blueprint("painel", __name__)

# Documentos que aparecem na lista do usuário (ficam em services.DocumentoService.BASE).
DOCUMENTOS = ("extrato.txt", "comprovante.txt")


def _conta(conexao):
    return ContaRepository(conexao).buscar(session["usuario_id"])


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = _conta(conexao)
    return render_template("painel.html", conta=conta, documentos=DOCUMENTOS, erro=None)


@painel_bp.get("/documento")
@login_obrigatorio
def documento():
    nome = request.args.get("nome", "")
    try:
        conteudo = DocumentoService().ler(nome)
    except (ValueError, OSError):
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            conta = _conta(conexao)
        return render_template(
            "painel.html", conta=conta, documentos=DOCUMENTOS, erro="Documento não encontrado."
        )
    return Response(conteudo, mimetype="text/plain")
