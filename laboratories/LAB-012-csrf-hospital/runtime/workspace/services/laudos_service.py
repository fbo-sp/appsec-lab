"""Camada de serviço: regras de alteração de e-mail para envio de laudos."""

import logging
import re

from models.usuario import Usuario
from repositories.historico_repository import HistoricoRepository
from repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger("laudos")

# E-mail no formato nome@provedor.dominio.
_FORMATO = re.compile('[^\\s@]+@[^\\s@]+\\.[a-z]{2,}')


class LaudosService:
    def __init__(self, usuarios: UsuarioRepository, historico: HistoricoRepository) -> None:
        self._usuarios = usuarios
        self._historico = historico

    def obter(self, usuario_id: int) -> tuple[Usuario, list]:
        return self._usuarios.buscar_por_id(usuario_id), self._historico.listar(usuario_id)

    def alterar(self, usuario_id: int, valor: str, origem: str) -> None:
        """Troca o e-mail de laudos e registra a alteração no histórico e no log.

        ``origem`` é o cabeçalho Sec-Fetch-Site que o navegador envia: de onde partiu a requisição.
        """
        valor = valor.strip()
        if not _FORMATO.fullmatch(valor):
            raise ValueError("Informe um e-mail válido, como nome@provedor.com.br.")
        usuario = self._usuarios.buscar_por_id(usuario_id)
        self._usuarios.alterar_email_laudos(usuario_id, valor)
        self._historico.registrar(usuario_id, usuario.email_laudos, valor)
        logger.info("Destino alterado: usuario=%s novo=%s origem=%s", usuario.login, valor, origem)
