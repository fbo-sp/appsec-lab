"""Camada de serviço: regras de negócio de favorecidos."""

import logging
import re

from config import Config
from models.favorecido import Favorecido
from repositories.favorecido_repository import FavorecidoRepository

_log = logging.getLogger("favorecidos")

# Proteção criada pelo time depois de um teste de invasão: remove a tag <script> do texto digitado.
_TAG_SCRIPT = re.compile(r"</?script[^>]*>", re.IGNORECASE)


class FavorecidoService:
    def __init__(self, repositorio: FavorecidoRepository) -> None:
        self._repositorio = repositorio

    @staticmethod
    def limpar_texto(texto: str) -> str:
        """Tira espaços das pontas, limita o tamanho e remove tags <script>."""
        return _TAG_SCRIPT.sub("", texto.strip())[: Config.TAMANHO_MAXIMO_BUSCA]

    def buscar(self, dono_id: int, termo: str) -> tuple[str, list[Favorecido]]:
        termo = self.limpar_texto(termo)
        return termo, self._repositorio.buscar_do_dono(dono_id, termo)

    def cadastrar(self, dono_id: int, nome: str, detalhe: str, nota: str) -> None:
        nome, detalhe, nota = (self.limpar_texto(v) for v in (nome, detalhe, nota))
        if not nome:
            raise ValueError("Informe o nome do favorecido.")
        self._repositorio.incluir(dono_id, nome, detalhe, nota)
        _log.info("Favorecido cadastrado pelo usuário %s: %s", dono_id, nome)

    def recentes(self) -> list[tuple[Favorecido, str]]:
        return self._repositorio.recentes()
