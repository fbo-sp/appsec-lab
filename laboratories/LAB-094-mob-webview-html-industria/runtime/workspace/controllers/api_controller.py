"""Camada de controle: a API que o app do celular chama. A falha deste laboratório está em services/mensagem_service.py e templates/webview_mensagens.html."""

import logging

from flask import Blueprint, current_app, jsonify, render_template, request

from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.item_repository import ItemRepository
from repositories.mensagem_repository import MensagemRepository
from repositories.token_repository import TokenRepository
from services.auth_service import AuthService
from services.identidade_service import IdentidadeService
from services.mensagem_service import MensagemInvalida, MensagemService

api_bp = Blueprint("api", __name__)
logger = logging.getLogger("api")


def _conexao():
    return abrir_conexao(current_app.config["CAMINHO_BANCO"])


def _token() -> str | None:
    """O token que o app envia no cabeçalho ``Authorization: Bearer <token>``."""
    cabecalho = request.headers.get("Authorization", "")
    return cabecalho[7:].strip() if cabecalho.startswith("Bearer ") else None


def _negado():
    return jsonify({"erro": "nao autorizado"}), 401


def conta_logada(conexao) -> int | None:
    """Id da conta do pedido, decidido pelo serviço de identidade."""
    return IdentidadeService(TokenRepository(conexao)).identificar(_token(), request.headers)


@api_bp.post("/api/login")
def login():
    """Confere usuário e senha e devolve um token de sessão para o app guardar."""
    dados = request.get_json(silent=True) or {}
    login, senha = str(dados.get("login", "")), str(dados.get("senha", ""))
    with _conexao() as conexao:
        conta = AuthService(ContaRepository(conexao)).autenticar(login, senha)
        if conta is None:
            logger.info("Login recusado: login=%s", login.strip().lower())
            return jsonify({"erro": "Usuario ou senha invalidos."}), 401
        token = TokenRepository(conexao).emitir(conta.id)
    logger.info("Login aceito: login=%s", conta.login)
    return jsonify({"token": token, "contaId": conta.id, "nome": conta.nome})


@api_bp.get("/api/conta")
def conta():
    """Nome e resumo da tela inicial do app."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        conta = ContaRepository(conexao).buscar(conta_id)
    return jsonify({"nome": conta.nome, "resumo": conta.resumo})


@api_bp.get("/api/itens")
def itens():
    """A lista da tela inicial (Ordens de serviço) do usuário logado."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        lista = ItemRepository(conexao).listar_do_dono(conta_id)
    return jsonify({"itens": [vars(i) for i in lista]})



@api_bp.post("/api/mensagens")
def enviar_mensagem():
    """Aviso de turno: o usuário logado escreve uma mensagem para outro usuário do app."""
    dados = request.get_json(silent=True) or {}
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        servico = MensagemService(MensagemRepository(conexao), ContaRepository(conexao))
        try:
            servico.enviar(conta_id, str(dados.get("para", "")), str(dados.get("texto", "")))
        except MensagemInvalida as erro:
            return jsonify({"erro": str(erro)}), 400
    logger.info("Mensagem enviada: de=%s", conta_id)
    return jsonify({"enviada": True})


@api_bp.get("/api/mensagens/pagina")
def pagina_mensagens():
    """A página da central de mensagens (Avisos de turno), que o app mostra num WebView."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        mensagens = MensagemService(MensagemRepository(conexao), ContaRepository(conexao)).da_conta(conta_id)
    return render_template("webview_mensagens.html", mensagens=mensagens)
