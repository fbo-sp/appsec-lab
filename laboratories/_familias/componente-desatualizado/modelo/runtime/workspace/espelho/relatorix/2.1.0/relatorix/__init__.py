"""relatorix 2.1.0: gerador de documentos para impressão a partir de modelos HTML.

Biblioteca FICTÍCIA, criada para o CECyber AppSec Labs (não existe no PyPI).
"""

import os
from string import Template
from urllib.parse import unquote

__version__ = "2.1.0"


class ModeloInvalido(ValueError):
    """O modelo pedido não existe ou não pode ser usado."""


class Gerador:
    def __init__(self, pasta_modelos: str) -> None:
        self.pasta_modelos = pasta_modelos

    def gerar(self, nome_modelo: str, dados: dict[str, str]) -> str:
        """Abre o modelo ``nome_modelo`` da pasta de modelos e preenche os campos ``$campo``."""
        # Aceita nomes vindos de links já codificados (ex.: "extrato%20mensal.html").
        nome = unquote(nome_modelo)
        caminho = os.path.join(self.pasta_modelos, nome)
        if not os.path.isfile(caminho):
            raise ModeloInvalido(f"Modelo não encontrado: {nome}")
        with open(caminho, encoding="utf-8") as arquivo:
            return Template(arquivo.read()).safe_substitute(dados)
