"""Camada de serviço: regras de alteração de celular do plantão."""

import logging
import re

from models.usuario import Usuario
from repositories.historico_repository import HistoricoRepository
from repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger("alarmes")

# Celular com +55 e DDD, só dígitos.
_FORMATO = re.compile('\\+55\\d{10,11}')


class AlarmesService:
    def __init__(self, usuarios: UsuarioRepository, historico: HistoricoRepository) -> None:
        self._usuarios = usuarios
        self._historico = historico

    def obter(self, usuario_id: int) -> tuple[Usuario, list]:
        return self._usuarios.buscar_por_id(usuario_id), self._historico.listar(usuario_id)

    def alterar(self, usuario_id: int, valor: str, origem: str) -> None:
        """Troca o celular do plantão e registra a alteração no histórico e no log.

        ``origem`` é o cabeçalho Sec-Fetch-Site que o navegador envia: de onde partiu a requisição.
        """
        valor = valor.strip()
        if not _FORMATO.fullmatch(valor):
            raise ValueError("Informe o celular com +55 e DDD, só dígitos. Exemplo: +5551999991234.")
        usuario = self._usuarios.buscar_por_id(usuario_id)
        self._usuarios.alterar_celular_plantao(usuario_id, valor)
        self._historico.registrar(usuario_id, usuario.celular_plantao, valor)
        logger.info("Destino alterado: usuario=%s novo=%s origem=%s", usuario.login, valor, origem)
