"""Camada de repositório: consultas da tabela de usuários."""

import sqlite3

from models.usuario import Usuario

_CAMPOS = "id, login, nome, [[campo]]"


class UsuarioRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_login(self, login: str) -> tuple[Usuario, str] | None:
        """Retorna o usuário e o hash da senha, ou None."""
        linha = self._conexao.execute(
            f"SELECT {_CAMPOS}, senha_hash FROM usuarios WHERE login = ?", (login,)
        ).fetchone()
        if linha is None:
            return None
        return Usuario(*linha[:-1]), linha[-1]

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        linha = self._conexao.execute(f"SELECT {_CAMPOS} FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        return Usuario(*linha) if linha else None

    def alterar_[[campo]](self, usuario_id: int, valor: str) -> None:
        self._conexao.execute("UPDATE usuarios SET [[campo]] = ? WHERE id = ?", (valor, usuario_id))
