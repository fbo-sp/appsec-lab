"""Camada de controle: a área logada do Console Interno e a API administrativa."""

from flask import Blueprint, current_app, jsonify, render_template, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from services.permissao_service import PermissaoService

painel_bp = Blueprint("painel", __name__)


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        conta = ContaRepository(conexao).buscar(session["usuario_id"])
    return render_template("painel.html", conta=conta)


@painel_bp.get("/api/admin/usuarios")
@login_obrigatorio
def admin_usuarios():
    """API administrativa: lista TODOS os usuários. Só o papel admin deveria poder usá-la."""
    papel = session.get("usuario_papel", "comum")
    if not PermissaoService().pode_administrar(papel):
        return jsonify({"erro": "acesso negado"}), 403
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        usuarios = ContaRepository(conexao).listar_todos()
    return jsonify(
        {"usuarios": [{"login": u.login, "nome": u.nome, "papel": u.papel} for u in usuarios]}
    )
