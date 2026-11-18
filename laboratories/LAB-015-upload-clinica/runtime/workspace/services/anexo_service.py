"""Camada de serviço: recebimento de pedidos médicos."""

import logging
import os

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import Config
from repositories.anexo_repository import AnexoRepository

logger = logging.getLogger("anexos")


class AnexoService:
    def __init__(self, repositorio: AnexoRepository) -> None:
        self._repositorio = repositorio

    def salvar(self, dono_id: int, descricao: str, arquivo: FileStorage | None) -> str:
        """Confere o tipo, grava o arquivo em /tmp/anexos e registra o envio. Devolve o nome gravado."""
        if arquivo is None or not arquivo.filename:
            raise ValueError("Escolha um arquivo para enviar.")
        # O navegador informa o tipo do arquivo (Content-Type) junto com o envio.
        if arquivo.mimetype not in Config.TIPOS_PERMITIDOS:
            raise ValueError("Envie um PDF, PNG ou JPEG.")
        nome = secure_filename(arquivo.filename)  # tira barras e "..": o arquivo não sai da pasta
        arquivo.save(os.path.join(Config.PASTA_ANEXOS, nome))
        self._repositorio.inserir(dono_id, descricao.strip()[:120], nome)
        logger.info("Anexo recebido: dono=%s arquivo=%s tipo_informado=%s", dono_id, nome, arquivo.mimetype)
        return nome
