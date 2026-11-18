"""Camada de controle: a API que o app do celular chama. A falha deste laboratório está em services/operacao_service.py."""

import logging

from flask import Blueprint, current_app, jsonify, request

from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from repositories.item_repository import ItemRepository
from repositories.operacao_repository import OperacaoRepository
from repositories.token_repository import TokenRepository
from services.auth_service import AuthService
from services.identidade_service import IdentidadeService
from services.operacao_service import OperacaoInvalida, OperacaoService

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
    """A lista da tela inicial (Meus exames) do usuário logado."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        lista = ItemRepository(conexao).listar_do_dono(conta_id)
    return jsonify({"itens": [vars(i) for i in lista]})


def _servico(conexao) -> OperacaoService:
    return OperacaoService(OperacaoRepository(conexao), current_app.config["VALIDADE_CONFIRMACAO_SEGUNDOS"])


def _dados_operacao() -> tuple[str, str]:
    dados = request.get_json(silent=True) or {}
    return str(dados.get("alvo", "")), str(dados.get("detalhe", ""))


@api_bp.get("/api/operacoes")
def operacoes():
    """Histórico de operações (compartilhamento de laudo) da conta, a mais recente primeiro."""
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        lista = OperacaoRepository(conexao).da_conta(conta_id)
    return jsonify({"operacoes": [{"alvo": o.alvo, "detalhe": o.detalhe, "status": o.status} for o in lista]})


@api_bp.post("/api/operacoes")
def iniciar():
    """Botão do app: cria a operação pendente; o app mostra a tela de confirmação."""
    alvo, detalhe = _dados_operacao()
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        try:
            resposta = _servico(conexao).iniciar(conta_id, alvo, detalhe)
        except OperacaoInvalida as erro:
            return jsonify({"erro": str(erro)}), 400
    logger.info("Operação pendente criada pelo app: conta=%s", conta_id)
    return jsonify(resposta)


@api_bp.post("/api/operacoes/rapida")
def rapida():
    """Chamada pelo app ao abrir um link lumen://compartilhar (deep link da campanha "um toque")."""
    alvo, detalhe = _dados_operacao()
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        try:
            resposta = _servico(conexao).iniciar_por_link(conta_id, alvo, detalhe)
        except OperacaoInvalida as erro:
            return jsonify({"erro": str(erro)}), 400
    logger.info("Operação por link: conta=%s status=%s", conta_id, resposta["status"])
    return jsonify(resposta)


@api_bp.post("/api/operacoes/confirmar")
def confirmar():
    """O usuário tocou em Confirmar: executa a operação pendente do código, uma única vez."""
    codigo = str((request.get_json(silent=True) or {}).get("confirmacao", ""))
    with _conexao() as conexao:
        conta_id = conta_logada(conexao)
        if conta_id is None:
            return _negado()
        try:
            resposta = _servico(conexao).confirmar(conta_id, codigo)
        except OperacaoInvalida as erro:
            return jsonify({"erro": str(erro)}), 409
    logger.info("Operação confirmada pelo usuário: conta=%s", conta_id)
    return jsonify(resposta)
