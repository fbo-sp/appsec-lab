"""Camada de controle: login e logout do Internet Banking."""

from functools import wraps

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from database.conexao import abrir_conexao
from repositories.cliente_repository import ClienteRepository
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


def login_obrigatorio(rota):
    """Só deixa passar quem fez login. Guarda o id do cliente em ``session["cliente_id"]``."""

    @wraps(rota)
    def verificar(*args, **kwargs):
        if "cliente_id" not in session:
            if request.path.startswith("/api/"):
                return {"erro": "login necessário"}, 401
            return redirect(url_for("auth.entrar"))
        return rota(*args, **kwargs)

    return verificar


@auth_bp.route("/login", methods=["GET", "POST"])
def entrar():
    erro = None
    if request.method == "POST":
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            cliente = AuthService(ClienteRepository(conexao)).autenticar(
                request.form.get("email", ""), request.form.get("senha", "")
            )
        if cliente is not None:
            session.clear()
            session["cliente_id"] = cliente.id
            session["cliente_nome"] = cliente.nome
            return redirect(url_for("comprovantes.listar"))
        erro = "E-mail ou senha inválidos."
    return render_template("login.html", erro=erro)


@auth_bp.get("/sair")
def sair():
    session.clear()
    return redirect(url_for("auth.entrar"))
