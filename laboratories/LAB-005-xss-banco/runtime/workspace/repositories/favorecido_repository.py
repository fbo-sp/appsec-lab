"""Camada de repositório: consultas de favorecidos.

As consultas usam parâmetros (``?``), então o texto digitado nunca vira SQL. A falha deste laboratório
está em outro lugar: na forma como esse texto volta para a página.
"""

import sqlite3

from models.favorecido import Favorecido

_COLUNAS = "id, dono_id, nome, detalhe, nota, criado_em"


class FavorecidoRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_do_dono(self, dono_id: int, termo: str) -> list[Favorecido]:
        linhas = self._conexao.execute(
            f"SELECT {_COLUNAS} FROM favorecidos WHERE dono_id = ? AND nome LIKE ? ORDER BY nome",
            (dono_id, f"%{termo}%"),
        ).fetchall()
        return [Favorecido(*linha) for linha in linhas]

    def incluir(self, dono_id: int, nome: str, detalhe: str, nota: str) -> None:
        self._conexao.execute(
            "INSERT INTO favorecidos (dono_id, nome, detalhe, nota) VALUES (?, ?, ?, ?)",
            (dono_id, nome, detalhe, nota),
        )

    def recentes(self, limite: int = 20) -> list[tuple[Favorecido, str]]:
        """Últimos favorecidos de todos os usuários, com o nome de quem cadastrou."""
        linhas = self._conexao.execute(
            f"SELECT {', '.join('e.' + c.strip() for c in _COLUNAS.split(','))}, u.nome "
            "FROM favorecidos e JOIN usuarios u ON u.id = e.dono_id ORDER BY e.id DESC LIMIT ?",
            (limite,),
        ).fetchall()
        return [(Favorecido(*linha[:6]), linha[6]) for linha in linhas]
