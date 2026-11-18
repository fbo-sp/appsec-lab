"""Camada de serviço: autenticação (quem é você?).

A autenticação NÃO é o foco deste laboratório; as senhas já são guardadas com hash forte (werkzeug).
A falha a encontrar e corrigir está na configuração de CORS da API (services/cors_service.py).
"""

from werkzeug.security import check_password_hash

from models.conta import Conta
from repositories.conta_repository import ContaRepository


class AuthService:
    def __init__(self, repositorio: ContaRepository) -> None:
        self._repositorio = repositorio

    def autenticar(self, login: str, senha: str) -> Conta | None:
        encontrado = self._repositorio.buscar_por_login(login.strip().lower())
        if encontrado is None:
            return None
        conta, senha_hash = encontrado
        if check_password_hash(senha_hash, senha):
            return conta
        return None
