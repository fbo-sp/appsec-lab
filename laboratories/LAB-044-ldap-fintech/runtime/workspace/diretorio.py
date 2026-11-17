"""Diretório corporativo SIMULADO + um avaliador mínimo de filtro no estilo LDAP.

Não há servidor LDAP real: as entradas são uma lista fixa e o "filtro" aceita só ``(cn=PADRÃO)``.
No PADRÃO, um ``*`` NÃO escapado é curinga (casa qualquer trecho); a sequência ``\\2a`` representa um
``*`` literal (é a forma escapada). É o suficiente para mostrar injeção de LDAP: se o nome do usuário
entrar cru no filtro, um ``*`` vira curinga e lista o diretório inteiro.
"""

from __future__ import annotations

import re

# (cn = nome comum, setor) — pessoas fictícias de um diretório corporativo.
ENTRADAS: list[tuple[str, str]] = [
    ('Ana Ribeiro Teixeira', 'Contas'),
    ('Carlos Moura Pinto', 'Crédito'),
    ('Juliana Alves Castro', 'Prevenção a Fraudes'),
    ('Rafael Dias Nogueira', 'Tesouraria'),
    ('Beatriz Lima Fontes', 'Atendimento'),
]


def _padrao_para_regex(padrao: str) -> str:
    """Traduz o PADRÃO (curinga ``*``; ``\\2a`` = ``*`` literal) para uma regex de correspondência total."""
    regex = ""
    i = 0
    while i < len(padrao):
        if padrao[i] == "\\" and padrao[i + 1 : i + 3].lower() == "2a":
            regex += re.escape("*")  # \2a = asterisco literal
            i += 3
        elif padrao[i] == "*":
            regex += ".*"  # curinga
            i += 1
        else:
            regex += re.escape(padrao[i])
            i += 1
    return regex


def buscar(filtro: str) -> list[dict[str, str]]:
    """Avalia um filtro ``(cn=PADRÃO)`` sobre o diretório e devolve as entradas que casam."""
    if not (filtro.startswith("(cn=") and filtro.endswith(")")):
        return []
    padrao = _padrao_para_regex(filtro[4:-1])
    return [
        {"cn": cn, "setor": setor} for cn, setor in ENTRADAS if re.fullmatch(padrao, cn) is not None
    ]
