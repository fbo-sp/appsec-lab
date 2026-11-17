"""Camada de controle: login e logout (não é o foco deste laboratório)."""

import logging
from functools import wraps

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from database.conexao import abrir_conexao
from repositories.conta_repository import ContaRepository
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger("auth")


def login_obrigatorio(rota):
    """Só deixa passar quem fez login. O id da conta fica em ``session["usuario_id"]``."""

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
        login = request.form.get("login", "")
        with abrir_conexao(current_app.config["CAMINHO_BANCO"]) as conexao:
            conta = AuthService(ContaRepository(conexao)).autenticar(login, request.form.get("senha", ""))
        if conta is not None:
            session.clear()
            session["usuario_id"] = conta.id
            session["usuario_nome"] = conta.nome
            logger.info("Login aceito: login=%s", conta.login)
            return redirect(url_for("painel.ver"))
        logger.info("Login recusado: login=%s", login.strip().lower())
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)


@auth_bp.get("/sair")
def sair():
    session.clear()
    return redirect(url_for("auth.entrar"))
