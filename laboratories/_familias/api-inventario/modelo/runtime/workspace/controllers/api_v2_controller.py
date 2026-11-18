"""Camada de controle: a API atual (v2) de [[recurso_plural]].

A v2 entrou em [[ano_v2]], depois de um teste de invasão, e confere o dono do documento no serviço.
"""

from flask import Blueprint, current_app, jsonify, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.documento_repository import DocumentoRepository
from services.documento_service import DocumentoService

api_v2_bp = Blueprint("api_v2", __name__)


@api_v2_bp.get("/api/v2/[[recurso]]/<int:doc_id>")
@login_obrigatorio
def buscar_v2(doc_id: int):
    """Devolve o documento só se ele for da conta logada."""
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        documento = DocumentoService(DocumentoRepository(conexao)).buscar_do_dono(doc_id, session["usuario_id"])
    if documento is None:
        return jsonify({"erro": "não encontrado"}), 404
    return jsonify(documento.como_dict())
