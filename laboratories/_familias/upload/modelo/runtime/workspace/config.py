"""Configurações da aplicação.

O banco, os anexos e o log ficam em /tmp, a única pasta gravável fora do workspace. Tudo é recriado a
cada vez que a aplicação inicia (inclusive quando você salva um arquivo .py).
"""


class Config:
    CAMINHO_BANCO = "/tmp/[[banco]].db"
    PASTA_ANEXOS = "/tmp/anexos"
    ARQUIVO_LOG = "/tmp/app.log"
    # Chave FICTÍCIA que assina o cookie de sessão do Flask (só existe neste laboratório).
    SECRET_KEY = "lab-[[imagem]]-chave-ficticia-de-treinamento"
    SESSION_COOKIE_HTTPONLY = True
    TEMPLATES_AUTO_RELOAD = True
    # Tamanho máximo de um envio (2 MiB): acima disso o Flask responde 413.
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    # Tipos de arquivo aceitos para [[documento_plural]].
    TIPOS_PERMITIDOS = {"application/pdf", "image/png", "image/jpeg"}
