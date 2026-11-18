"""[[app_nome]] · [[empresa]].

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de atribuição em massa (mass assignment) para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                     |
                     +-> templates/ (monta o HTML de resposta)
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.area_controller import area_bp
from controllers.auth_controller import auth_bp, usuario_atual
from controllers.perfil_controller import perfil_bp
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
    app.json.sort_keys = Config.JSON_SORT_KEYS
    app.register_blueprint(auth_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(area_bp)

    @app.context_processor
    def dados_do_topo():
        # O menu mostra a [[area_priv_titulo]] só para quem tem o perfil "[[perfil_priv]]".
        return {"usuario": usuario_atual()}

    @app.get("/")
    def inicio():
        return redirect(url_for("perfil.ver"))

    return app


app = criar_app()
