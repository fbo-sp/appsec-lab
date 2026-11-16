"""Camada de controle: login e logout."""

from functools import wraps

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from database.conexao import abrir_conexao
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


def usuario_atual() -> Usuario | None:
    """Lê o usuário logado do banco (ou None)."""
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return None
    with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
        return UsuarioRepository(conexao).buscar_por_id(usuario_id)


def login_obrigatorio(rota):
    """Só deixa passar quem fez login. O id do usuário fica em ``session["usuario_id"]``."""

    @wraps(rota)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.entrar"))
        return rota(*args, **kwargs)

    return verificar


@auth_bp.route("/login", methods=["GET", "POST"])
def entrar():
    erro = None
    if request.method == "POST":
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            usuario = AuthService(UsuarioRepository(conexao)).autenticar(
                request.form.get("login", ""), request.form.get("senha", "")
            )
        if usuario is not None:
            session.clear()
            session["usuario_id"] = usuario.id
            return redirect(url_for("laudos.ver"))
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)


@auth_bp.get("/sair")
def sair():
    session.clear()
    return redirect(url_for("auth.entrar"))
