"""Camada de acesso a dados dos comprovantes de PIX."""

import sqlite3

from models.comprovante import Comprovante

_CAMPOS = """
    SELECT p.id, p.cliente_id, p.data_hora, p.valor_centavos, p.recebedor_nome,
           p.recebedor_documento, p.chave_pix, p.id_transacao,
           c.nome, c.documento, c.agencia, c.conta
      FROM pix_enviados p
      JOIN clientes c ON c.id = p.cliente_id
"""


class ComprovanteRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def listar_do_cliente(self, cliente_id: int) -> list[Comprovante]:
        """Comprovantes de um cliente, do mais recente para o mais antigo."""
        linhas = self._conexao.execute(
            _CAMPOS + " WHERE p.cliente_id = ? ORDER BY p.id DESC", (cliente_id,)
        ).fetchall()
        return [Comprovante(*linha) for linha in linhas]

    def buscar_por_id(self, comprovante_id: int) -> Comprovante | None:
        """Comprovante com o número informado."""
        linha = self._conexao.execute(_CAMPOS + " WHERE p.id = ?", (comprovante_id,)).fetchone()
        return Comprovante(*linha) if linha else None
