"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia (inclusive quando você salva um arquivo .py), então você pode testar à vontade.
"""


class Config:
    CAMINHO_BANCO = "/tmp/[[banco]].db"
    ARQUIVO_LOG = "/tmp/app.log"
    # Chave FICTÍCIA que assina o cookie de sessão do Flask (só existe neste laboratório).
    SECRET_KEY = "lab-[[imagem]]-chave-ficticia-de-treinamento"
    SESSION_COOKIE_HTTPONLY = True
    # Chave FICTÍCIA combinada com o [[fornecedor]] para assinar os pacotes (HMAC-SHA256). Em produção,
    # ela fica num cofre de segredos, nunca no código.
    CHAVE_FORNECEDOR = "[[chave_fornecedor]]"
    MAX_CONTENT_LENGTH = 64 * 1024  # um pacote de parâmetros é pequeno
    TEMPLATES_AUTO_RELOAD = True
