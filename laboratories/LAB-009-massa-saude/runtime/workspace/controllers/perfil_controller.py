"""Camada de controle: tela Meu perfil e a API que ela usa."""

from flask import Blueprint, current_app, jsonify, render_template, request, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.usuario_repository import UsuarioRepository
from services.perfil_service import PerfilService

perfil_bp = Blueprint("perfil", __name__)


def _servico(conexao) -> PerfilService:
    return PerfilService(UsuarioRepository(conexao))


@perfil_bp.get("/perfil")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        servico = _servico(conexao)
        usuario = servico.obter(session["usuario_id"])
        descricao = servico.descrever(usuario)
    return render_template("perfil.html", dados=usuario, descricao=descricao)


@perfil_bp.get("/api/perfil")
@login_obrigatorio
def obter():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        usuario = _servico(conexao).obter(session["usuario_id"])
    return jsonify(usuario.como_dict())


@perfil_bp.patch("/api/perfil")
@login_obrigatorio
def atualizar():
    dados = request.get_json(silent=True)
    try:
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            usuario = _servico(conexao).atualizar_perfil(session["usuario_id"], dados)
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    return jsonify(usuario.como_dict())
