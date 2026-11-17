"""Camada de controle: o painel do Portal de Exames e a API GraphQL de pedidos."""

import logging

from flask import Blueprint, current_app, jsonify, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.pedido_repository import PedidoRepository
from services.pedido_service import PedidoService

painel_bp = Blueprint("painel", __name__)
logger = logging.getLogger("painel")


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
    return render_template("painel.html", conta=conta)


@painel_bp.post("/graphql")
@login_obrigatorio
def graphql():
    """API GraphQL (simplificada): resolve a query ``pedido(id: N)`` para o usuário logado.

    Aceita um corpo JSON ``{"query": "...", "variables": {"id": N}}``. Para o laboratório ficar
    direto, só a operação ``pedido`` é suportada e o id vem de ``variables.id`` (o texto da query é
    ilustrativo). O que importa é que o resolver chama o serviço com o id do usuário logado.
    """
    dados = request.get_json(silent=True) or {}
    variaveis = dados.get("variables") or {}
    try:
        pedido_id = int(variaveis.get("id"))
    except (TypeError, ValueError):
        return jsonify({"errors": [{"message": "variables.id é obrigatório e deve ser inteiro"}]}), 400

    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        pedido = PedidoService(PedidoRepository(conexao)).resolver(session["usuario_id"], pedido_id)

    if pedido is None:
        logger.info("GraphQL pedido negado: usuario=%s pedido=%s", session["usuario_id"], pedido_id)
        return jsonify({"data": {"pedido": None}, "errors": [{"message": "acesso negado"}]})
    logger.info("GraphQL pedido resolvido: usuario=%s pedido=%s", session["usuario_id"], pedido_id)
    return jsonify(
        {"data": {"pedido": {"id": pedido.id, "descricao": pedido.descricao, "valor": pedido.valor}}}
    )
