"""Modelo: uma nota fiscal enviado por um usuário."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Anexo:
    id: int
    dono: str  # nome de quem enviou
    descricao: str
    nome_arquivo: str  # nome do arquivo em /tmp/anexos
    enviado_em: str
