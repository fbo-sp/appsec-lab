"""Camada de repositório: os parâmetros em vigor e o pacote que os trouxe."""

import sqlite3


class ParametroRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def em_vigor(self) -> list[tuple[str, str, str, str]]:
        """(nome, descrição, valor, unidade) de cada parâmetro."""
        return self._conexao.execute(
            "SELECT nome, descricao, valor, unidade FROM parametros ORDER BY nome"
        ).fetchall()

    def pacote_atual(self) -> tuple[str, str]:
        """(versão, fornecedor) do último pacote aplicado."""
        return self._conexao.execute("SELECT versao, fornecedor FROM pacote_atual").fetchone()

    def substituir(self, versao: str, fornecedor: str, parametros: dict) -> None:
        """Grava os valores do pacote nos parâmetros conhecidos e registra a versão aplicada."""
        for nome, valor in parametros.items():
            self._conexao.execute("UPDATE parametros SET valor = ? WHERE nome = ?", (str(valor), str(nome)))
        self._conexao.execute("UPDATE pacote_atual SET versao = ?, fornecedor = ?", (versao, fornecedor))
        self._conexao.commit()
