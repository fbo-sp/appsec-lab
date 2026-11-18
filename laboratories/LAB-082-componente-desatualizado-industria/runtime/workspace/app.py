"""Ferro Norte Manutenção · Siderúrgica Ferro Norte.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, um **componente com falha conhecida** (OWASP A06:2021 / A03:2025) para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                       |
                       +-> templates/ (monta o HTML de resposta)

O documento para impressão é montado pela biblioteca relatorix, na versão fixada em requirements.txt
e carregada do espelho interno (dependencias.py). A falha não está no código da aplicação: a versão
fixada da biblioteca tem uma falha conhecida, publicada no aviso de segurança em avisos/.
"""

import logging

import dependencias

VERSOES = dependencias.carregar()  # antes de qualquer import que use os pacotes do espelho interno

from flask import Flask, redirect, url_for  # noqa: E402

from config import Config  # noqa: E402
from controllers.auth_controller import auth_bp  # noqa: E402
from controllers.painel_controller import painel_bp  # noqa: E402
from database.seed import criar_banco  # noqa: E402


def configurar_logs() -> None:
    """Envia os logs para a saída do processo, que o comando de início copia para /tmp/app.log."""
    destino = logging.StreamHandler()
    destino.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    raiz.addHandler(destino)


def criar_app() -> Flask:
    configurar_logs()
    logging.getLogger("dependencias").info("Pacotes do espelho interno: %s", VERSOES)
    criar_banco(Config.CAMINHO_BANCO)

    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(auth_bp)
    app.register_blueprint(painel_bp)

    @app.get("/")
    def inicio():
        return redirect(url_for("painel.ver"))

    return app


app = criar_app()
