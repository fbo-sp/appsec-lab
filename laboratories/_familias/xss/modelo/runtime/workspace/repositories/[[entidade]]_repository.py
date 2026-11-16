"""Camada de repositório: consultas de [[entidades_label]].

As consultas usam parâmetros (``?``), então o texto digitado nunca vira SQL. A falha deste laboratório
está em outro lugar: na forma como esse texto volta para a página.
"""

import sqlite3

from models.[[entidade]] import [[Entidade]]

_COLUNAS = "id, dono_id, nome, detalhe, nota, criado_em"


class [[Entidade]]Repository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_do_dono(self, dono_id: int, termo: str) -> list[[[Entidade]]]:
        linhas = self._conexao.execute(
            f"SELECT {_COLUNAS} FROM [[tabela]] WHERE dono_id = ? AND nome LIKE ? ORDER BY nome",
            (dono_id, f"%{termo}%"),
        ).fetchall()
        return [[[Entidade]](*linha) for linha in linhas]

    def incluir(self, dono_id: int, nome: str, detalhe: str, nota: str) -> None:
        self._conexao.execute(
            "INSERT INTO [[tabela]] (dono_id, nome, detalhe, nota) VALUES (?, ?, ?, ?)",
            (dono_id, nome, detalhe, nota),
        )

    def recentes(self, limite: int = 20) -> list[tuple[[[Entidade]], str]]:
        """Últim[[genero]]s [[entidades_label]] de todos os usuários, com o nome de quem cadastrou."""
        linhas = self._conexao.execute(
            f"SELECT {', '.join('e.' + c.strip() for c in _COLUNAS.split(','))}, u.nome "
            "FROM [[tabela]] e JOIN usuarios u ON u.id = e.dono_id ORDER BY e.id DESC LIMIT ?",
            (limite,),
        ).fetchall()
        return [([[Entidade]](*linha[:6]), linha[6]) for linha in linhas]
