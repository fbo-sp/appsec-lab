"""Camada de serviço: regras de negócio de [[entidades_label]]."""

import logging
import re

from config import Config
from models.[[entidade]] import [[Entidade]]
from repositories.[[entidade]]_repository import [[Entidade]]Repository

_log = logging.getLogger("[[entidade]]s")

# Proteção criada pelo time depois de um teste de invasão: remove a tag <script> do texto digitado.
_TAG_SCRIPT = re.compile(r"</?script[^>]*>", re.IGNORECASE)


class [[Entidade]]Service:
    def __init__(self, repositorio: [[Entidade]]Repository) -> None:
        self._repositorio = repositorio

    @staticmethod
    def limpar_texto(texto: str) -> str:
        """Tira espaços das pontas, limita o tamanho e remove tags <script>."""
        return _TAG_SCRIPT.sub("", texto.strip())[: Config.TAMANHO_MAXIMO_BUSCA]

    def buscar(self, dono_id: int, termo: str) -> tuple[str, list[[[Entidade]]]]:
        termo = self.limpar_texto(termo)
        return termo, self._repositorio.buscar_do_dono(dono_id, termo)

    def cadastrar(self, dono_id: int, nome: str, detalhe: str, nota: str) -> None:
        nome, detalhe, nota = (self.limpar_texto(v) for v in (nome, detalhe, nota))
        if not nome:
            raise ValueError("Informe [[artigo_entidade]] [[label_nome_minusculo]].")
        self._repositorio.incluir(dono_id, nome, detalhe, nota)
        _log.info("[[Entidade]] cadastrad[[genero]] pelo usuário %s: %s", dono_id, nome)

    def recentes(self) -> list[tuple[[[Entidade]], str]]:
        return self._repositorio.recentes()
