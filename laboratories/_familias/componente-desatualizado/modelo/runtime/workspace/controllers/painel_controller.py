"""Camada de controle: a área logada do [[app_nome]] e a geração do documento para impressão."""

import relatorix
from flask import Blueprint, Response, current_app, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.item_repository import ItemRepository
from services.documento_service import DocumentoService

painel_bp = Blueprint("painel", __name__)

# Modelos oferecidos na tela (ficam em /workspace/modelos).
MODELOS = (("padrao.html", "Padrão"), ("detalhado.html", "Detalhado"))


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
        itens = ItemRepository(conexao).da_conta(session["usuario_id"])
    return render_template(
        "painel.html", conta=conta, itens=itens, modelos=MODELOS, versao=relatorix.__version__, erro=None
    )


@painel_bp.get("/documento")
@login_obrigatorio
def documento():
    modelo = request.args.get("modelo", "padrao.html")
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
        itens = ItemRepository(conexao).da_conta(session["usuario_id"])
    try:
        conteudo = DocumentoService().gerar(modelo, conta, itens)
    except (ValueError, OSError):
        return render_template(
            "painel.html",
            conta=conta,
            itens=itens,
            modelos=MODELOS,
            versao=relatorix.__version__,
            erro="Modelo de documento não encontrado.",
        ), 404
    return Response(conteudo, mimetype="text/html")
