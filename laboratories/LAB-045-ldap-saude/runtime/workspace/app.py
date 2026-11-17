"""Diretório de Profissionais · Clínica Lumen.

Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
propósito, uma falha de segurança na **busca de pessoas no diretório** para você encontrar e corrigir.

Como ela está organizada (veja também o README.md):

    navegador -> controllers/ -> services/ -> diretorio.py (diretório simulado)
                     |
                     +-> templates/ (monta o HTML de resposta)

O funcionário faz login e, no painel, busca colegas pelo nome. A busca monta um filtro no estilo
LDAP a partir do nome digitado e consulta o diretório. A falha a corrigir está em
services/busca_service.py: o nome entra CRU no filtro, então um ``*`` digitado vira curinga e lista
o diretório inteiro — é injeção de LDAP.
"""

import logging

from flask import Flask, redirect, url_for

from config import Config
from controllers.auth_controller import auth_bp
from controllers.painel_controller import painel_bp
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

    @app.get("/")
    def inicio():
        return redirect(url_for("painel.ver"))

    return app


app = criar_app()
