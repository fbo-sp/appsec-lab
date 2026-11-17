"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia (inclusive quando você salva um arquivo .py), então você pode testar à vontade.
"""


class Config:
    CAMINHO_BANCO = "/tmp/pagomais_mobile.db"
    ARQUIVO_LOG = "/tmp/app.log"
    TEMPLATES_AUTO_RELOAD = True
    # Recursos da tela do app usados neste laboratório.
    RECURSOS = []
    # O "aparelho" simulado: as preferências que o app grava no celular.
    CAMINHO_DISPOSITIVO = "/tmp/dispositivo.db"
