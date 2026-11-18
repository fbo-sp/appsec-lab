"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia (inclusive quando você salva um arquivo .py), então você pode testar à vontade.
"""


class Config:
    CAMINHO_BANCO = "/tmp/trilhapay.db"
    ARQUIVO_LOG = "/tmp/app.log"
    # Chave FICTÍCIA que assina o cookie de sessão do Flask (só existe neste laboratório).
    SECRET_KEY = "lab-lab-008-massa-chave-ficticia-de-treinamento"
    SESSION_COOKIE_HTTPONLY = True
    TEMPLATES_AUTO_RELOAD = True
    # Respostas JSON com os campos na ordem em que foram montados (mais fácil de ler no terminal).
    JSON_SORT_KEYS = False
