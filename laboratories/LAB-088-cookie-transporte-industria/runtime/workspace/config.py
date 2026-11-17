"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia (inclusive quando você salva um arquivo .py), então você pode testar à vontade.

Em produção, o Ipê Telemetria de Subestações roda atrás do balanceador da Transmissora Ipê Energia, que recebe o HTTPS e
repassa para esta aplicação. O cookie de sessão e os cabeçalhos de segurança, porém, são definidos aqui.
"""


class Config:
    CAMINHO_BANCO = "/tmp/ipe_telemetria.db"
    ARQUIVO_LOG = "/tmp/app.log"
    # Chave FICTÍCIA que assina o cookie de sessão do Flask (só existe neste laboratório).
    SECRET_KEY = "lab-lab-088-cookie-transporte-chave-ficticia-de-treinamento"
    TEMPLATES_AUTO_RELOAD = True

    # Cookie de sessão. Estas opções vêm da época em que o portal rodava só na rede interna, por HTTP.
    SESSION_COOKIE_NAME = "session"
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False  # o antigo aviso de "sessão expirando" lia o cookie pelo JavaScript
    SESSION_COOKIE_SAMESITE = None

    # Cabeçalhos de segurança que a aplicação envia em toda resposta (veja app.py).
    CABECALHOS_SEGURANCA = {
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "same-origin",
    }
