"""Serra Azul Empresas · Elétrica Serra Azul.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de **inventário de API** para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador / app -> controllers/ -> services/ -> repositories/ -> banco SQLite
                           |
                           +-> templates/ (monta o HTML de resposta)

A API de faturas tem duas versões registradas abaixo. A v2 é a atual e confere o dono do
documento. A v1 (legada) continua registrada e no ar. A falha a corrigir está em
controllers/api_v1_controller.py.
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.api_v1_controller import api_v1_bp
from controllers.api_v2_controller import api_v2_bp
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
    app.register_blueprint(api_v2_bp)
    # Versão 1 da API, de 2022. O app Serra Azul Empresas 1.x antigo ainda chama esta versão.
    app.register_blueprint(api_v1_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("painel.ver"))

    return app


app = criar_app()
