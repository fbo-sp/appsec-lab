"""Camada de controle: login e logout."""

from functools import wraps

from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for

from database.conexao import abrir_conexao
from repositories.usuario_repository import UsuarioRepository
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

# Cookies que o front-end antigo lê com JavaScript, por isso SEM HttpOnly (veja "Explorar mais").
COOKIE_CLIENTE = "[[cookie_cliente]]"  # [[segredo_cliente_desc]]
COOKIE_EQUIPE = "[[cookie_staff]]"  # [[segredo_staff_desc]]


def login_obrigatorio(rota):
    """Só deixa passar quem fez login. O id do usuário fica em ``session["usuario_id"]``."""

    @wraps(rota)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.entrar"))
        return rota(*args, **kwargs)

    return verificar


def equipe_obrigatoria(rota):
    """Só a equipe interna ([[staff_cargo]]) acessa."""

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
            resposta = redirect(url_for(destino))
            nome_cookie = COOKIE_EQUIPE if usuario.eh_equipe else COOKIE_CLIENTE
            resposta.set_cookie(nome_cookie, usuario.segredo, httponly=False, samesite="Lax")
            return resposta
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)


@auth_bp.get("/sair")
def sair():
    session.clear()
    resposta = redirect(url_for("auth.entrar"))
    resposta.delete_cookie(COOKIE_CLIENTE)
    resposta.delete_cookie(COOKIE_EQUIPE)
    return resposta
