"""Camada de repositório: consultas da tabela de faturas."""

import sqlite3

from models.documento import Documento

_CAMPOS = "d.id, d.conta_id, c.nome, d.titulo, d.data, d.detalhe"


class DocumentoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar(self, doc_id: int) -> Documento | None:
        """Busca pelo id, sem olhar o dono. Quem chama decide se a conta pode ver."""
        linha = self._conexao.execute(
            f"SELECT {_CAMPOS} FROM documentos d JOIN contas c ON c.id = d.conta_id WHERE d.id = ?", (doc_id,)
        ).fetchone()
        return Documento(*linha) if linha else None

    def listar_da_conta(self, conta_id: int) -> list[Documento]:
        linhas = self._conexao.execute(
            f"SELECT {_CAMPOS} FROM documentos d JOIN contas c ON c.id = d.conta_id WHERE d.conta_id = ? ORDER BY d.id",
            (conta_id,),
        ).fetchall()
        return [Documento(*linha) for linha in linhas]
