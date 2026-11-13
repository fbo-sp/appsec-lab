"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia, então você pode testar à vontade.
"""


class Config:
    CAMINHO_BANCO = "/tmp/clinica.db"
    ARQUIVO_LOG = "/tmp/app.log"
    # Tamanho máximo do termo de busca aceito pelo serviço.
    TAMANHO_MAXIMO_BUSCA = 120
