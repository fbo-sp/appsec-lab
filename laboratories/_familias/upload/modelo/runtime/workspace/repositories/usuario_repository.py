"""Camada de repositório: consultas da tabela de usuários."""

import sqlite3

from models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_login(self, login: str) -> tuple[Usuario, str] | None:
        """Retorna o usuário e o hash da senha, ou None."""
        linha = self._conexao.execute(
            "SELECT id, login, nome, perfil, senha_hash FROM usuarios WHERE login = ?", (login,)
        ).fetchone()
        if linha is None:
            return None
        return Usuario(*linha[:4]), linha[4]

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        linha = self._conexao.execute(
            "SELECT id, login, nome, perfil FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return Usuario(*linha) if linha else None
