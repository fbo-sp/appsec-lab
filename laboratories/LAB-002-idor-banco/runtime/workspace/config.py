"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia, então você pode testar à vontade.
"""


class Config:
    CAMINHO_BANCO = "/tmp/banco.db"
    ARQUIVO_LOG = "/tmp/app.log"
    # Chave que assina o cookie de sessão. Valor FICTÍCIO de laboratório: em produção ela viria de um
    # cofre de segredos, nunca do código.
    SECRET_KEY = "chave-ficticia-do-laboratorio-lab002"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
