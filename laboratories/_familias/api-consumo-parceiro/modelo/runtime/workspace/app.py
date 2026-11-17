"""[[app_nome]] · [[empresa]].

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de **consumo inseguro de API** (OWASP API10) para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                                     |
                                     +-> services/parceiro_client.py -> API do [[parceiro_nome]]

A resposta do parceiro é gravada por services/consulta_service.py. A falha a corrigir está lá: ele
confia no que o parceiro devolve, sem conferir o contrato combinado.
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.auth_controller import auth_bp
from controllers.painel_controller import painel_bp
from controllers.parceiro_simulado import parceiro_bp
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
    # Simulação do parceiro (só existe no laboratório, no lugar da API externa).
    app.register_blueprint(parceiro_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("painel.ver"))

    return app


app = criar_app()
