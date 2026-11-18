"""Camada de serviço: autenticação (quem é você?).

O resumo de senha abaixo veio do sistema legado "[[sistema_legado]]" e foi mantido na migração para
que as contas importadas continuassem entrando com a mesma senha.
"""

import hashlib

from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository


class AuthService:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def _resumo(self, senha: str) -> str:
        """Resume a senha para comparar com o que está guardado no banco."""
        return hashlib.md5(senha.encode()).hexdigest()

    def autenticar(self, login: str, senha: str) -> Usuario | None:
        encontrado = self._repositorio.buscar_por_login(login.strip().lower())
        if encontrado is None:
            return None
        usuario, senha_hash = encontrado
        # O usuário entra se o resumo da senha digitada for igual ao resumo guardado.
        if self._resumo(senha) == senha_hash:
            return usuario
        return None
