"""Camada de serviço: regras de negócio de ordens de serviço."""

import logging
import re

from config import Config
from models.ordem import Ordem
from repositories.ordem_repository import OrdemRepository

_log = logging.getLogger("ordems")

# Proteção criada pelo time depois de um teste de invasão: remove a tag <script> do texto digitado.
_TAG_SCRIPT = re.compile(r"</?script[^>]*>", re.IGNORECASE)


class OrdemService:
    def __init__(self, repositorio: OrdemRepository) -> None:
        self._repositorio = repositorio

    @staticmethod
    def limpar_texto(texto: str) -> str:
        """Tira espaços das pontas, limita o tamanho e remove tags <script>."""
        return _TAG_SCRIPT.sub("", texto.strip())[: Config.TAMANHO_MAXIMO_BUSCA]

    def buscar(self, dono_id: int, termo: str) -> tuple[str, list[Ordem]]:
        termo = self.limpar_texto(termo)
        return termo, self._repositorio.buscar_do_dono(dono_id, termo)

    def cadastrar(self, dono_id: int, nome: str, detalhe: str, nota: str) -> None:
        nome, detalhe, nota = (self.limpar_texto(v) for v in (nome, detalhe, nota))
        if not nome:
            raise ValueError("Informe a equipamento.")
        self._repositorio.incluir(dono_id, nome, detalhe, nota)
        _log.info("Ordem cadastrada pelo usuário %s: %s", dono_id, nome)

    def recentes(self) -> list[tuple[Ordem, str]]:
        return self._repositorio.recentes()
