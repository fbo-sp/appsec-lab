"""relatorix 2.4.1: gerador de documentos para impressão a partir de modelos HTML.

Biblioteca FICTÍCIA, criada para o CECyber AppSec Labs (não existe no PyPI).
"""

import os
from string import Template
from urllib.parse import unquote

__version__ = "2.4.1"


class ModeloInvalido(ValueError):
    """O modelo pedido não existe ou não pode ser usado."""


class Gerador:
    def __init__(self, pasta_modelos: str) -> None:
        self.pasta_modelos = pasta_modelos

    def gerar(self, nome_modelo: str, dados: dict[str, str]) -> str:
        """Abre o modelo ``nome_modelo`` da pasta de modelos e preenche os campos ``$campo``."""
        # Aceita nomes vindos de links já codificados (ex.: "extrato%20mensal.html").
        nome = unquote(nome_modelo)
        # 2.4.1 (AVISO-2026-031): o caminho final precisa ficar DENTRO da pasta de modelos,
        # conferido depois de decodificar e de resolver "..", links e caminhos absolutos.
        base = os.path.realpath(self.pasta_modelos)
        caminho = os.path.realpath(os.path.join(base, nome))
        if not caminho.startswith(base + os.sep) or not os.path.isfile(caminho):
            raise ModeloInvalido("Modelo não encontrado.")
        with open(caminho, encoding="utf-8") as arquivo:
            return Template(arquivo.read()).safe_substitute(dados)
