"""Mesa de Crédito · Cooperativa Credimova.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de **SSRF** (Server-Side Request Forgery) para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> (busca servidor) -> serviços internos simulados
                     |
                     +-> templates/ (monta o HTML de resposta)

Dois serviços internos simulados sobem junto com a aplicação (interno/servicos.py), só em loopback:
o Serviço de Documentos (destino legítimo) e o Console de Infraestrutura (uso interno).
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.auth_controller import auth_bp
from controllers.importador_controller import importador_bp
from interno import servicos


def configurar_logs() -> None:
    """Envia os logs para a saída do processo, que o comando de início copia para /tmp/app.log."""
    destino = logging.StreamHandler()
    destino.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    raiz.addHandler(destino)


def criar_app() -> Flask:
    configurar_logs()
    servicos.iniciar()  # sobe os serviços internos simulados (loopback)

    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(auth_bp)
    app.register_blueprint(importador_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("importador.form"))

    return app


app = criar_app()
