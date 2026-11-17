"""Camada de controle: a versão 1 (legada) da API de exames. É AQUI que mora a falha.

A v1 é de 2021. Quando a v2 foi publicada, a v1 saiu da documentação, mas ninguém a desligou:
a rota continua registrada em app.py e responde para qualquer usuário logado. Ela busca o documento
direto no repositório, pelo id, sem passar pelo serviço que confere o dono. Uma versão esquecida no
ar, fora do inventário, é a falha "gestão de inventário inadequada" (OWASP API9).
"""

from flask import Blueprint, current_app, jsonify

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.documento_repository import DocumentoRepository

api_v1_bp = Blueprint("api_v1", __name__)


@api_v1_bp.get("/api/v1/exames/<int:doc_id>")
@login_obrigatorio
def buscar_v1(doc_id: int):
    """Versão 1 (legada): devolve o documento pelo id, de qualquer conta."""
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        documento = DocumentoRepository(conexao).buscar(doc_id)
    if documento is None:
        return jsonify({"erro": "não encontrado"}), 404
    return jsonify(documento.como_dict())
