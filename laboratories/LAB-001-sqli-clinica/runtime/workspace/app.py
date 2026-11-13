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


def configurar_logs(arquivo: str) -> None:
    """Envia os logs para o terminal do contêiner e para um arquivo que você pode ler."""
    formato = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    for destino in (logging.StreamHandler(), logging.FileHandler(arquivo, encoding="utf-8")):
        destino.setFormatter(formato)
        raiz.addHandler(destino)


def criar_app() -> Flask:
    configurar_logs(Config.ARQUIVO_LOG)
    criar_banco(Config.CAMINHO_BANCO)

    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(medicos_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("medicos.buscar"))

    return app


app = criar_app()
