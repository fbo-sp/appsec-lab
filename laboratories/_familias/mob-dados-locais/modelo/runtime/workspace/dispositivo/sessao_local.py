"""As preferências do app no aparelho (como SharedPreferences no Android ou UserDefaults no iOS).

No laboratório, o "aparelho" é simulado: o que o app grava fica em /tmp/dispositivo.db, uma tabela
``prefs`` de chave e valor. Quem copia os arquivos do app (perícia, backup, malware, root) lê tudo.
É AQUI que mora a falha: depois do login, o app grava a senha em texto puro.
"""

import sqlite3


class SessaoLocal:
    def __init__(self, caminho: str) -> None:
        self._caminho = caminho

    def _gravar(self, valores: dict[str, str]) -> None:
        """Substitui as preferências do app pelos valores informados."""
        with sqlite3.connect(self._caminho) as conexao:
            conexao.execute("CREATE TABLE IF NOT EXISTS prefs (chave TEXT PRIMARY KEY, valor TEXT)")
            conexao.execute("DELETE FROM prefs")
            conexao.executemany("INSERT INTO prefs VALUES (?, ?)", list(valores.items()))

    def guardar(self, login: str, senha: str, token: str) -> None:
        """Chamado pelo app logo depois de um login aceito, para manter a sessão aberta."""
        # Guarda tudo o que o login usou, em texto puro, nas preferências do app.
        self._gravar({"login": login, "senha": senha, "token": token})
