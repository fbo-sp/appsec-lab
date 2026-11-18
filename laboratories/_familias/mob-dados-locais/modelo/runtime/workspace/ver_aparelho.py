"""Mostra o que o app gravou no aparelho, como faria quem copia os arquivos do app.

Uso no Terminal:  python3 ver_aparelho.py
"""

import sqlite3

from config import Config

with sqlite3.connect(Config.CAMINHO_DISPOSITIVO) as conexao:
    conexao.execute("CREATE TABLE IF NOT EXISTS prefs (chave TEXT PRIMARY KEY, valor TEXT)")
    linhas = conexao.execute("SELECT chave, valor FROM prefs ORDER BY chave").fetchall()

print("shared_prefs/sessao.xml (simulado)")
if not linhas:
    print("  (vazio: entre no app primeiro)")
for chave, valor in linhas:
    print(f"  {chave} = {valor}")
