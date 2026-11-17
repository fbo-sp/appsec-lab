"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia (inclusive quando você salva um arquivo .py), então você pode testar à vontade.
"""

import os


class Config:
    CAMINHO_BANCO = "/tmp/bemcuidar_reembolso.db"
    ARQUIVO_LOG = "/tmp/app.log"
    # Chave FICTÍCIA que assina o cookie de sessão do Flask (só existe neste laboratório).
    SECRET_KEY = "lab-lab-072-api-consumo-chave-ficticia-de-treinamento"
    SESSION_COOKIE_HTTPONLY = True
    TEMPLATES_AUTO_RELOAD = True
    # API do parceiro. No laboratório ela é SIMULADA dentro do próprio contêiner (controllers/parceiro_simulado.py),
    # sem acesso à internet; num sistema real seria o endereço do Rede Atlas Credenciados.
    URL_PARCEIRO = f"http://127.0.0.1:{os.environ.get('LAB_PORTA', '8080')}/parceiro/api"
    ARQUIVO_MODO_PARCEIRO = "/tmp/parceiro_modo.txt"
