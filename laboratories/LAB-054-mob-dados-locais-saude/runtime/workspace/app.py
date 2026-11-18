"""App Lumen Saúde · Clínica Lumen — app MOBILE de treinamento (ADR-025).

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de segurança para você encontrar e corrigir. A falha está em dispositivo/sessao_local.py (veja o README.md).

Como ela está organizada (veja também o README.md):

    app no celular (templates/ + static/app.js) -> API: controllers/ -> services/ -> repositories/ -> SQLite

O app que aparece na moldura de celular da aba Aplicação é um cliente web mobile simulado: ele fala
com a API do servidor exatamente como um app Android ou iOS falaria.
"""

import logging

from flask import Flask, render_template

from config import Config
from controllers.api_controller import api_bp
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
    app.register_blueprint(api_bp)

    @app.get("/")
    def tela():
        """A tela do app no celular (moldura de celular na aba Aplicação)."""
        return render_template("app.html", recursos=Config.RECURSOS)

    return app


app = criar_app()
