"""Camada de repositório: consultas da tabela de usuários."""

import sqlite3

from models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_login(self, login: str) -> tuple[Usuario, str] | None:
        """Retorna o usuário e o hash da senha guardado no banco, ou None."""
        linha = self._conexao.execute(
            "SELECT id, login, nome, senha_hash FROM usuarios WHERE login = ?", (login,)
        ).fetchone()
        if linha is None:
            return None
        return Usuario(*linha[:-1]), linha[-1]

    def hash_da_senha(self, usuario_id: int) -> str | None:
        """O hash da senha como está guardado agora (para mostrar o formato no painel)."""
        linha = self._conexao.execute(
            "SELECT senha_hash FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return linha[0] if linha else None

    def atualizar_senha(self, usuario_id: int, senha_hash: str) -> None:
        self._conexao.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?", (senha_hash, usuario_id)
        )
