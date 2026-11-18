"""Nébula Cartões Online · Nébula Cartões.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de **proteção da sessão no transporte** (OWASP A02:2021 / A04:2025) para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                       |
                       +-> templates/ (monta o HTML de resposta)

Depois do login, quem é você fica num cookie de sessão. A falha a corrigir está em config.py: o
cookie sai sem as flags Secure, HttpOnly e SameSite, e a aplicação não envia o cabeçalho HSTS.
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
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
    app.register_blueprint(auth_bp)
    app.register_blueprint(painel_bp)

    @app.after_request
    def cabecalhos_de_seguranca(resposta):
        """Acrescenta a toda resposta os cabeçalhos de Config.CABECALHOS_SEGURANCA."""
        for nome, valor in app.config["CABECALHOS_SEGURANCA"].items():
            resposta.headers.setdefault(nome, valor)
        return resposta

    @app.get("/")
    def inicio():
        return redirect(url_for("painel.ver"))

    return app


app = criar_app()
