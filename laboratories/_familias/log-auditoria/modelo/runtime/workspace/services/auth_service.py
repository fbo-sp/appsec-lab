"""Camada de serviço: autenticação (quem é você?). É AQUI que mora a falha.

O time de monitoramento investiga ataques pela trilha de AUDITORIA (tabela ``auditoria``): quem tentou
entrar, de qual endereço, quando e com qual resultado. A falha: este serviço só registra o login que
deu certo. Tentativas com senha errada não deixam rastro, então um ataque que testa centenas de
senhas numa conta passa em silêncio. É a falha de registro e monitoramento (OWASP A09).

As senhas já são guardadas com hash forte (werkzeug); a senha digitada nunca deve ir para a auditoria.
"""

from werkzeug.security import check_password_hash

from models.conta import Conta
from repositories.auditoria_repository import AuditoriaRepository
from repositories.conta_repository import ContaRepository


class AuthService:
    def __init__(self, contas: ContaRepository, auditoria: AuditoriaRepository) -> None:
        self._contas = contas
        self._auditoria = auditoria

    def autenticar(self, login: str, senha: str, ip: str) -> Conta | None:
        """Confere login e senha e devolve a conta (ou None se não baterem)."""
        login = login.strip().lower()
        encontrado = self._contas.buscar_por_login(login)
        if encontrado is None:
            return None
        conta, senha_hash = encontrado
        if check_password_hash(senha_hash, senha):
            self._auditoria.registrar("login_ok", login, ip)
            return conta
        return None
