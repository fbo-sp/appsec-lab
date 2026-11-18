"""Camada de controle: os parâmetros de linha em vigor no Cruzeiro Parâmetros de Linha e a importação de pacotes."""

import logging

from flask import Blueprint, current_app, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.parametro_repository import ParametroRepository
from services.pacote_service import PacoteInvalido, PacoteService

painel_bp = Blueprint("painel", __name__)
log = logging.getLogger("pacotes")


def _tela(conexao, mensagem=None, erro=None, status=200):
    repositorio = ParametroRepository(conexao)
    return render_template(
        "painel.html",
        conta=ContaRepository(conexao).buscar(session["usuario_id"]),
        parametros=repositorio.em_vigor(),
        pacote=repositorio.pacote_atual(),
        mensagem=mensagem,
        erro=erro,
    ), status


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        return _tela(conexao)


@painel_bp.post("/pacotes")
@login_obrigatorio
def importar():
    arquivo = request.files.get("arquivo")
    texto = arquivo.read().decode("utf-8", errors="replace") if arquivo else ""
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = PacoteService(ParametroRepository(conexao), current_app.config["CHAVE_FORNECEDOR"])
        try:
            pacote = servico.importar(texto)
        except PacoteInvalido as erro:
            log.warning("Pacote recusado: %s", erro)
            return _tela(conexao, erro=f"Pacote recusado: {erro}", status=400)
        log.info("Pacote aplicado: versão %s", pacote["versao"])
        return _tela(conexao, mensagem=f"Pacote {pacote['versao']} aplicado.")
