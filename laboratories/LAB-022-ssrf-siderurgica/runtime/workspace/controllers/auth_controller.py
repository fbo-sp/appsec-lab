"""Camada de controller: login e logout da equipe interna."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
_servico = AuthService()


@auth_bp.get("/login")
def login_form():
    if session.get("usuario"):
        return redirect(url_for("importador.form"))
    return render_template("login.html", erro=None)


@auth_bp.post("/login")
def login():
    usuario = _servico.autenticar(request.form.get("login", ""), request.form.get("senha", ""))
    if usuario is None:
        return render_template("login.html", erro="Login ou senha inválidos."), 401
    session["usuario"] = usuario
    return redirect(url_for("importador.form"))


@auth_bp.get("/sair")
def sair():
    session.clear()
    return redirect(url_for("auth.login_form"))
