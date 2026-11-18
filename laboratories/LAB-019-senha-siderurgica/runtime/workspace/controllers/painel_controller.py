"""Camada de controle: a área logada do Portal do Colaborador."""

from flask import Blueprint, current_app, render_template, session

from controllers.auth_controller import login_obrigatorio
from database.conexao import abrir_conexao
from repositories.usuario_repository import UsuarioRepository

painel_bp = Blueprint("painel", __name__)

# Prefixos dos formatos de hash fortes (com sal e custo), gerados pelo werkzeug.
FORMATOS_FORTES = ("scrypt:", "pbkdf2:")


@painel_bp.get("/painel")
@login_obrigatorio
def ver():
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        senha_hash = UsuarioRepository(conexao).hash_da_senha(session["usuario_id"])
    reforcada = bool(senha_hash) and senha_hash.startswith(FORMATOS_FORTES)
    return render_template("painel.html", reforcada=reforcada)
