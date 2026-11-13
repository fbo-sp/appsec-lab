"""Internet Banking do Banco Vértice Digital.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de controle de acesso (IDOR) para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.auth_controller import auth_bp
from controllers.comprovantes_controller import comprovantes_bp
from database.seed import criar_banco


def configurar_logs() -> None:
    """Envia os logs para a saída de erro do processo.

    O comando que inicia a aplicação copia essa saída para ``Config.ARQUIVO_LOG`` (/tmp/app.log).
    """
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
    # JSON legível no terminal: acentos como texto e campos na ordem em que foram montados.
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    app.register_blueprint(auth_bp)
    app.register_blueprint(comprovantes_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("comprovantes.listar"))

    return app


app = criar_app()
