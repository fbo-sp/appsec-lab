"""Camada de controle: a API que o app do celular chama. A falha deste laboratório está em services/acao_service.py."""

import logging

from flask import Blueprint, current_app, jsonify, request

from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.item_repository import ItemRepository
from repositories.token_repository import TokenRepository
from services.auth_service import AuthService
from repositories.prova_repository import ProvaRepository
from services.acao_service import AcaoService

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
    """A lista da tela inicial (Ordens de serviço) do usuário logado."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        lista = ItemRepository(conexao).listar_do_dono(conta_id)
    return jsonify({"itens": [vars(i) for i in lista]})


@api_bp.post("/api/biometria/prova")
def prova_biometria():
    """Papel do chip seguro do aparelho: o app só chama depois que o sensor confirma a digital."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        prova = ProvaRepository(conexao).emitir(conta_id)
    return jsonify({"prova": prova})


@api_bp.post("/api/acao")
def acao():
    """A operação sensível (Liberar manobra no disjuntor 7). O app envia a prova da digital em X-Prova-Biometria."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        try:
            status = AcaoService(ProvaRepository(conexao)).executar(
                conta_id, request.headers.get("X-Prova-Biometria")
            )
        except PermissionError:
            logger.info("Operacao recusada sem prova valida: conta=%s", conta_id)
            return jsonify({"erro": "autenticacao recente exigida"}), 401
    return jsonify({"status": status, "acao": "Liberar manobra no disjuntor 7"})
