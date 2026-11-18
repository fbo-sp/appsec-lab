"""Camada de serviço: autenticação do cliente (quem é você?)."""

from werkzeug.security import check_password_hash

from models.cliente import Cliente
from repositories.cliente_repository import ClienteRepository


class AuthService:
    def __init__(self, repositorio: ClienteRepository) -> None:
        self._repositorio = repositorio

    def autenticar(self, email: str, senha: str) -> Cliente | None:
        """Retorna o cliente se e-mail e senha conferem."""
        encontrado = self._repositorio.buscar_por_email(email.strip().lower())
        if encontrado is None:
            return None
        cliente, senha_hash = encontrado
        return cliente if check_password_hash(senha_hash, senha) else None
