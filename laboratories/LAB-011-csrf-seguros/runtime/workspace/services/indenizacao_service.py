"""Camada de serviço: regras de alteração de chave PIX de indenização."""

import logging
import re

from models.usuario import Usuario
from repositories.historico_repository import HistoricoRepository
from repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger("indenizacao")

# Chave PIX: e-mail, CPF (11 dígitos) ou celular com +55.
_FORMATO = re.compile('[^\\s@]+@[^\\s@]+\\.[a-z]{2,}|\\d{11}|\\+55\\d{10,11}')


class IndenizacaoService:
    def __init__(self, usuarios: UsuarioRepository, historico: HistoricoRepository) -> None:
        self._usuarios = usuarios
        self._historico = historico

    def obter(self, usuario_id: int) -> tuple[Usuario, list]:
        return self._usuarios.buscar_por_id(usuario_id), self._historico.listar(usuario_id)

    def alterar(self, usuario_id: int, valor: str, origem: str) -> None:
        """Troca a chave PIX e registra a alteração no histórico e no log.

        ``origem`` é o cabeçalho Sec-Fetch-Site que o navegador envia: de onde partiu a requisição.
        """
        valor = valor.strip()
        if not _FORMATO.fullmatch(valor):
            raise ValueError("Informe uma chave PIX válida: e-mail, CPF (11 dígitos) ou celular com +55.")
        usuario = self._usuarios.buscar_por_id(usuario_id)
        self._usuarios.alterar_chave_pix(usuario_id, valor)
        self._historico.registrar(usuario_id, usuario.chave_pix, valor)
        logger.info("Destino alterado: usuario=%s novo=%s origem=%s", usuario.login, valor, origem)
