"""Camada de repositório: registros dos anexos enviados."""

import sqlite3

from models.anexo import Anexo

_CONSULTA = (
    "SELECT a.id, u.nome, a.descricao, a.nome_arquivo, a.enviado_em FROM anexos a"
    " JOIN usuarios u ON u.id = a.dono_id"
)


class AnexoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def inserir(self, dono_id: int, descricao: str, nome_arquivo: str) -> None:
        self._conexao.execute(
            "INSERT INTO anexos (dono_id, descricao, nome_arquivo) VALUES (?, ?, ?)",
            (dono_id, descricao, nome_arquivo),
        )

    def listar_do_dono(self, dono_id: int) -> list[Anexo]:
        linhas = self._conexao.execute(_CONSULTA + " WHERE a.dono_id = ? ORDER BY a.id DESC", (dono_id,))
        return [Anexo(*linha) for linha in linhas]

    def listar_todos(self) -> list[Anexo]:
        return [Anexo(*linha) for linha in self._conexao.execute(_CONSULTA + " ORDER BY a.id DESC")]
