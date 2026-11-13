"""Portal de agendamento da Clínica VidaPlena.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de SQL Injection para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.medicos_controller import medicos_bp
from database.seed import criar_banco


def configurar_logs() -> None:
    """Envia os logs para a saída de erro do processo.

    O comando que inicia a aplicação copia essa saída para ``Config.ARQUIVO_LOG`` (/tmp/app.log), então
    erros que acontecem antes desta função rodar, como um ``IndentationError``, também aparecem lá.
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
    app.register_blueprint(medicos_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("medicos.buscar"))

    return app


app = criar_app()
