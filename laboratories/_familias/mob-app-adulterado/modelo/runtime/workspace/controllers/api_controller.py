"""Camada de controle: a API que o app do celular chama. A falha deste laboratório está em services/recurso_service.py."""

import logging

from flask import Blueprint, current_app, jsonify, request

from database.conexao import abrir_conexao
from repositories.assinatura_repository import AssinaturaRepository
from repositories.conta_repository import ContaRepository
from repositories.item_repository import ItemRepository
from repositories.token_repository import TokenRepository
from services.atestacao_service import AtestacaoService
from services.auth_service import AuthService
from services.identidade_service import IdentidadeService
from services.recurso_service import RecursoService

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
    """Id da conta do pedido, decidido pelo serviço de identidade (cabeçalho Authorization)."""
    return IdentidadeService(TokenRepository(conexao)).identificar(_token())


def _atestacao() -> AtestacaoService:
    return AtestacaoService(current_app.config["PASTA_LOJA"], current_app.config["PASTA_APP"])


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
        plano = AssinaturaRepository(conexao).plano_da_conta(conta_id)
    return jsonify({"nome": conta.nome, "resumo": conta.resumo, "plano": plano})


@api_bp.get("/api/itens")
def itens():
    """A lista da tela inicial ([[lista_titulo]]) do usuário logado."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        lista = ItemRepository(conexao).listar_do_dono(conta_id)
    return jsonify({"itens": [vars(i) for i in lista]})


@api_bp.post("/api/atestacao")
def atestacao():
    """O app pede o selo de integridade (aqui, ao serviço da loja SIMULADO) antes de usar o recurso."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
    if conta_id is None:
        return _negado()
    return jsonify({"selo": _atestacao().emitir(conta_id)})


@api_bp.post("/api/recurso")
def recurso():
    """[[recurso_titulo]]: só para contas do plano avançado ([[plano_nome]])."""
    dados = request.get_json(silent=True) or {}
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        liberado = RecursoService(AssinaturaRepository(conexao), _atestacao()).liberar(conta_id, dados)
    logger.info("Recurso avancado: conta=%s plano_informado=%s liberado=%s", conta_id, dados.get("plano"), liberado)
    if not liberado:
        return jsonify({"liberado": False, "erro": "Recurso não liberado para esta conta."}), 403
    return jsonify({"liberado": True, "recurso": "[[recurso_titulo]]", "detalhe": "[[recurso_resultado]]"})
