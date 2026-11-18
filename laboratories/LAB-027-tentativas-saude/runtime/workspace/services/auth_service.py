"""Camada de serviço: autenticação do login. É AQUI que mora a falha deste laboratório.

As senhas já são guardadas com hash forte (werkzeug), então adivinhar o hash não é o problema. O
problema é de OUTRO tipo: quantas vezes seguidas alguém pode errar a senha? Este serviço confere a
senha e devolve a conta — mas não conta as tentativas. Sem um limite, um atacante testa senha após
senha (força bruta), sem parar, até acertar. A defesa é limitar as tentativas por usuário.
"""

from werkzeug.security import check_password_hash

from models.conta import Conta
from repositories.conta_repository import ContaRepository


class AuthService:
    def __init__(self, repositorio: ContaRepository) -> None:
        self._repositorio = repositorio

    def autenticar(self, login: str, senha: str) -> Conta | None:
        """Confere login e senha e devolve a conta (ou None se não baterem)."""
        encontrado = self._repositorio.buscar_por_login(login.strip().lower())
        if encontrado is None:
            return None
        conta, senha_hash = encontrado
        if check_password_hash(senha_hash, senha):
            return conta
        return None
