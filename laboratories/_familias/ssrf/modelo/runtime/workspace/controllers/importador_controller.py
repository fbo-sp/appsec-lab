"""Camada de controller: a tela de importar documento por URL.

O analista cola a URL do documento no sistema parceiro e a aplicação busca a prévia. A decisão de
segurança — para onde o servidor pode ou não buscar — fica no serviço (services/importador_service.py).
"""

import urllib.error

from flask import Blueprint, redirect, render_template, request, session, url_for

from services.importador_service import ImportadorService

importador_bp = Blueprint("importador", __name__)
_servico = ImportadorService()


def _logado() -> bool:
    return bool(session.get("usuario"))


@importador_bp.get("/importar")
def form():
    if not _logado():
        return redirect(url_for("auth.login_form"))
    return render_template("importar.html", previa=None, erro=None, url="")


@importador_bp.post("/importar")
def importar():
    if not _logado():
        return redirect(url_for("auth.login_form"))
    url = request.form.get("url", "").strip()
    try:
        previa = _servico.importar(url)
    except (ValueError, OSError, urllib.error.URLError) as erro:
        return render_template("importar.html", previa=None, erro=str(erro), url=url)
    return render_template("importar.html", previa=previa, erro=None, url=url)
