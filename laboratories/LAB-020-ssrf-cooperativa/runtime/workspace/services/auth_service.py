"""Camada de serviço: autenticação da equipe interna (quem é você?).

A autenticação NÃO é o foco deste laboratório; as senhas já são guardadas com hash forte (werkzeug).
A falha a encontrar e corrigir está no importador (services/importador_service.py).
"""

from werkzeug.security import check_password_hash, generate_password_hash

# Equipe interna fictícia que usa a mesa/painel (login, senha, nome, papel).
_SEED = [
    ("analista.credito", "Analista#Cred26", "Marina Aguiar Gomes", "Analista de crédito"),
    ("supervisor.mesa", "Supervisor#Cred26", "Rodrigo Sena Vilela", "Supervisor da mesa"),
]
_USUARIOS = {
    login: {"nome": nome, "papel": papel, "hash": generate_password_hash(senha)}
    for login, senha, nome, papel in _SEED
}


class AuthService:
    def autenticar(self, login: str, senha: str) -> dict[str, str] | None:
        chave = login.strip().lower()
        usuario = _USUARIOS.get(chave)
        if usuario and check_password_hash(usuario["hash"], senha):
            return {"login": chave, "nome": usuario["nome"], "papel": usuario["papel"]}
        return None
