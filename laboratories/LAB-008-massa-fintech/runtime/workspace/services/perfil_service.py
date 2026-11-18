"""Camada de serviço: regras da tela Meu perfil."""

import logging

from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger("perfil")

# O que cada valor de pacote significa para o cliente.
DESCRICOES = {
    "essencial": "limite de PIX de R$ 2.000,00 por dia",
    "private": "limite de PIX de R$ 250.000,00 por dia, sem tarifas",
}


class PerfilService:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def obter(self, usuario_id: int) -> Usuario | None:
        return self._repositorio.buscar_por_id(usuario_id)

    @staticmethod
    def descrever(usuario: Usuario) -> str:
        return DESCRICOES.get(usuario.pacote, "Não informado")

    def atualizar_perfil(self, usuario_id: int, dados: dict) -> Usuario:
        """Atualiza os dados de contato do próprio usuário (tela Meu perfil).

        A tela só envia e-mail e telefone, então o JSON recebido vai direto para o repositório.
        """
        if not isinstance(dados, dict) or not dados:
            raise ValueError("Envie em JSON os campos que quer atualizar.")
        self._validar_contato(dados)
        self._repositorio.atualizar(usuario_id, dados)
        logger.info("Perfil atualizado: usuario=%s campos=%s", usuario_id, sorted(dados))
        return self._repositorio.buscar_por_id(usuario_id)

    @staticmethod
    def _validar_contato(dados: dict) -> None:
        if "email" in dados and "@" not in str(dados["email"]):
            raise ValueError("E-mail inválido.")
        if "telefone" in dados and len(str(dados["telefone"])) > 30:
            raise ValueError("Telefone muito longo.")
