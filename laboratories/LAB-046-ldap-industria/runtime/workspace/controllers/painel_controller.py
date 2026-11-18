"""Camada de controle: o painel do Diretório de Equipe e a busca de pessoas no diretório."""

import logging

from flask import Blueprint, current_app, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from services.busca_service import BuscaService

painel_bp = Blueprint("painel", __name__)
logger = logging.getLogger("painel")


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
    return render_template("painel.html", conta=conta, nome=None, pessoas=None)


@painel_bp.get("/buscar")
@login_obrigatorio
def buscar():
    """Busca pessoas no diretório pelo nome digitado e mostra o resultado no painel."""
    nome = request.args.get("nome", "")
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
    pessoas = BuscaService().por_nome(nome) if nome else []
    logger.info("Busca no diretorio: nome=%r resultados=%d", nome, len(pessoas))
    return render_template("painel.html", conta=conta, nome=nome, pessoas=pessoas)
