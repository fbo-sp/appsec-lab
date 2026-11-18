"""Pináculo Invest · Corretora Pináculo.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de **consumo irrestrito de recursos** (OWASP API4) para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador / app -> controllers/ -> services/ -> repositories/ -> banco SQLite

A API de lançamentos aceita o tamanho de página que o cliente pedir. A falha a corrigir está em
services/lancamento_service.py.
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.api_controller import api_bp
from controllers.auth_controller import auth_bp
from controllers.painel_controller import painel_bp
from database.seed import criar_banco


def configurar_logs() -> None:
    """Envia os logs para a saída do processo, que o comando de início copia para /tmp/app.log."""
    destino = logging.StreamHandler()
    destino.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    raiz.addHandler(destino)


def criar_app() -> Flask:
    configurar_logs()
    criar_banco(Config.CAMINHO_BANCO)

    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False  # o JSON mostra acentos como texto, legível no navegador
    app.register_blueprint(auth_bp)
    app.register_blueprint(painel_bp)
    app.register_blueprint(api_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("painel.ver"))

    return app


app = criar_app()
