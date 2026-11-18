"""Camada de controle: a API de atendimentos que o app e as integrações chamam."""

import logging
import time

from flask import Blueprint, current_app, jsonify, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.atendimento_repository import AtendimentoRepository
from services.atendimento_service import AtendimentoService

api_bp = Blueprint("api", __name__)
logger = logging.getLogger("api")


@api_bp.get("/api/atendimentos")
@login_obrigatorio
def listar():
    """Lista os atendimentos da conta. Parâmetros: ``limite`` (itens por página) e ``pagina``."""
    try:
        limite = int(request.args.get("limite", "20"))
        pagina = int(request.args.get("pagina", "1"))
    except ValueError:
        return jsonify({"erro": "limite e pagina devem ser números inteiros"}), 400
    inicio = time.perf_counter()
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        itens = AtendimentoService(AtendimentoRepository(conexao)).listar(session["usuario_id"], limite, pagina)
    ms = (time.perf_counter() - inicio) * 1000
    logger.info("Listagem: limite=%s pagina=%s itens=%s tempo_ms=%.1f", limite, pagina, len(itens), ms)
    return jsonify({"pagina": pagina, "quantidade": len(itens), "itens": [i.como_dict() for i in itens]})
