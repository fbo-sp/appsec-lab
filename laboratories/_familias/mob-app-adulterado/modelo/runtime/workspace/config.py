"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia (inclusive quando você salva um arquivo .py), então você pode testar à vontade.
"""

import os


class Config:
    CAMINHO_BANCO = "/tmp/[[banco]].db"
    ARQUIVO_LOG = "/tmp/app.log"
    TEMPLATES_AUTO_RELOAD = True
    # Serviço de integridade SIMULADO (a "loja"): hash do pacote oficial e chave do selo, fora do workspace.
    PASTA_LOJA = "/opt/loja"
    PASTA_APP = os.path.dirname(os.path.abspath(__file__))
    # Recursos da tela do app usados neste laboratório.
    RECURSOS = ['recurso_premium']
