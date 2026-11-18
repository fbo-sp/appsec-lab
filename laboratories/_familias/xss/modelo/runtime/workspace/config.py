"""Configurações da aplicação.

O banco e o log ficam em /tmp, a única pasta gravável fora do workspace. O banco é recriado a cada
vez que a aplicação inicia, então você pode testar à vontade.
"""


class Config:
    CAMINHO_BANCO = "/tmp/[[banco]].db"
    ARQUIVO_LOG = "/tmp/app.log"
    # Chave FICTÍCIA que assina o cookie de sessão do Flask (só existe neste laboratório).
    SECRET_KEY = "lab-[[imagem]]-chave-ficticia-de-treinamento"
    # O cookie de sessão do Flask já sai com HttpOnly: o JavaScript da página não consegue lê-lo.
    SESSION_COOKIE_HTTPONLY = True
    # Templates salvos no editor valem na hora, sem reiniciar a aplicação.
    TEMPLATES_AUTO_RELOAD = True
    TAMANHO_MAXIMO_BUSCA = 120
