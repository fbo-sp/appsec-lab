"""Camada de controle: a API que o app do celular chama. A falha deste laboratório está em services/acesso_service.py."""

import logging

from flask import Blueprint, current_app, jsonify, request

from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.item_repository import ItemRepository
from repositories.token_repository import TokenRepository
from services.auth_service import AuthService
from services.acesso_service import AcessoService

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
    """Id da conta dona do token enviado pelo app, ou None."""
    token = _token()
    return TokenRepository(conexao).conta_do_token(token) if token else None


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
    """A lista da tela inicial ([[lista_titulo]]) da conta pedida em ``?conta=``."""
    try:
        conta_id = int(request.args.get("conta", ""))
    except ValueError:
        return jsonify({"erro": "informe ?conta=<id>"}), 400
    chave = request.headers.get("X-Api-Key")
    with _conexao() as conexao:
        acesso = AcessoService(TokenRepository(conexao), current_app.config["CHAVE_DO_APP"])
        if not acesso.conta_autorizada(chave, _token(), conta_id):
            logger.info("Lista negada: conta=%s", conta_id)
            return _negado()
        lista = ItemRepository(conexao).listar_do_dono(conta_id)
    logger.info("Lista entregue: conta=%s", conta_id)
    return jsonify({"itens": [vars(i) for i in lista]})
