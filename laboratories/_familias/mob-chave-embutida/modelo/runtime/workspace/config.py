"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia (inclusive quando você salva um arquivo .py), então você pode testar à vontade.
"""


class Config:
    CAMINHO_BANCO = "/tmp/[[banco]].db"
    ARQUIVO_LOG = "/tmp/app.log"
    TEMPLATES_AUTO_RELOAD = True
    # Recursos da tela do app usados neste laboratório.
    RECURSOS = ['chave']
    # Chave do app, a mesma que vai empacotada em cliente/config.json.
    CHAVE_DO_APP = "[[chave_app]]"
