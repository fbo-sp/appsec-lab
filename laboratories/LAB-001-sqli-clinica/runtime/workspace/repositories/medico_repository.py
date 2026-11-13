"""Camada de acesso a dados: é aqui que o SQL é montado e executado."""

import sqlite3

from models.medico import Medico


class MedicoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_nome(self, termo: str) -> list[Medico]:
        """Retorna os médicos cujo nome contém ``termo``."""
        sql = f"SELECT id, nome, especialidade, crm FROM medicos WHERE nome LIKE '%{termo}%'"
        linhas = self._conexao.execute(sql).fetchall()
        return [Medico(*linha) for linha in linhas]
