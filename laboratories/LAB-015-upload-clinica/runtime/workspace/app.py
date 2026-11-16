"""Portal de Agendamento · Clínica Sampaio.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de upload de arquivo que leva a XSS armazenado, para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                     |               |
                     |               +-> /tmp/anexos (os arquivos enviados)
                     +-> templates/ (monta o HTML de resposta)
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.anexo_controller import anexo_bp
from controllers.auth_controller import auth_bp
from controllers.mesa_controller import mesa_bp
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
    criar_banco(Config.CAMINHO_BANCO, Config.PASTA_ANEXOS)

    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(auth_bp)
    app.register_blueprint(anexo_bp)
    app.register_blueprint(mesa_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("anexo.enviar"))

    return app


app = criar_app()
