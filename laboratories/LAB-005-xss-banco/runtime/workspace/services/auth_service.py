"""Camada de serviço: autenticação (quem é você?)."""

from werkzeug.security import check_password_hash

from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository


class AuthService:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def autenticar(self, login: str, senha: str) -> Usuario | None:
        encontrado = self._repositorio.buscar_por_login(login.strip().lower())
        if encontrado is None:
            return None
        usuario, senha_hash = encontrado
        return usuario if check_password_hash(senha_hash, senha) else None
