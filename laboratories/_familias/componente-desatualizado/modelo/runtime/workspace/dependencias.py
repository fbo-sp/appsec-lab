"""Carrega as dependências do espelho interno, na versão fixada em requirements.txt.

No dia a dia, o ``pip install -r requirements.txt`` baixa cada pacote na versão fixada, de um
repositório interno (Artifactory, Nexus). O laboratório não tem internet, então este módulo faz o
papel do pip para os pacotes internos: lê a versão fixada de cada pacote e usa a pasta
correspondente em ``espelho/<pacote>/<versão>/``. Não é preciso mexer neste arquivo.
"""

import os
import re
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
ESPELHO = os.path.join(PASTA, "espelho")
_FIXADO = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([A-Za-z0-9_.-]+)")


def versoes_fixadas() -> dict[str, str]:
    versoes = {}
    with open(os.path.join(PASTA, "requirements.txt"), encoding="utf-8") as arquivo:
        for linha in arquivo:
            achado = _FIXADO.match(linha.split("#", 1)[0])
            if achado:
                versoes[achado.group(1).lower()] = achado.group(2)
    return versoes


def carregar() -> dict[str, str]:
    """Põe no caminho de importação a versão fixada de cada pacote do espelho interno."""
    carregados = {}
    for pacote, versao in versoes_fixadas().items():
        pasta = os.path.join(ESPELHO, pacote, versao)
        if os.path.isdir(os.path.join(ESPELHO, pacote)):
            if not os.path.isdir(pasta):
                disponiveis = ", ".join(sorted(os.listdir(os.path.join(ESPELHO, pacote))))
                raise RuntimeError(f"{pacote}=={versao} não está no espelho interno (há: {disponiveis})")
            sys.path.insert(0, pasta)
            carregados[pacote] = versao
    return carregados
