"""Portal de Manutenção da Ferrara Metais, Planta Contagem.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios, os CLPs são simulados e
ela contém, de propósito, uma falha de Command Injection para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> infra/ (comandos do sistema operacional)
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.diagnostico_controller import diagnostico_bp


def configurar_logs() -> None:
    """Envia os logs para a saída de erro do processo, copiada para /tmp/app.log."""
    destino = logging.StreamHandler()
    destino.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    raiz.addHandler(destino)


def criar_app() -> Flask:
    configurar_logs()
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(diagnostico_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("diagnostico.testar"))

    return app


app = criar_app()
