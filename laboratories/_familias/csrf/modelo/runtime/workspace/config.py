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
    # Incluído depois do último teste de invasão: "com SameSite=Lax o navegador não manda o cookie
    # de sessão em formulários vindos de outros sites, então CSRF está resolvido".
    SESSION_COOKIE_SAMESITE = "Lax"
    TEMPLATES_AUTO_RELOAD = True
