"""Camada de controle: login e logout."""

from functools import wraps

from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for

from database.conexao import abrir_conexao
from repositories.usuario_repository import UsuarioRepository
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


def login_obrigatorio(rota):
    """Só deixa passar quem fez login. O id do usuário fica em ``session["usuario_id"]``."""

    @wraps(rota)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.entrar"))
        return rota(*args, **kwargs)

    return verificar


def equipe_obrigatoria(rota):
    """Só a equipe interna (analistas de crédito) acessa."""

    @wraps(rota)
    def verificar(*args, **kwargs):
        if session.get("perfil") != "equipe":
            abort(403)
        return rota(*args, **kwargs)

    return login_obrigatorio(verificar)


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
            session["usuario_nome"] = usuario.nome
            session["perfil"] = usuario.perfil
            destino = "mesa.listar" if usuario.eh_equipe else "anexo.enviar"
            return redirect(url_for(destino))
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)


@auth_bp.get("/sair")
def sair():
    session.clear()
    return redirect(url_for("auth.entrar"))
