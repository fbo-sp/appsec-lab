"""Camada de repositório: consultas de exames.

As consultas usam parâmetros (``?``), então o texto digitado nunca vira SQL. A falha deste laboratório
está em outro lugar: na forma como esse texto volta para a página.
"""

import sqlite3

from models.exame import Exame

_COLUNAS = "id, dono_id, nome, detalhe, nota, criado_em"


class ExameRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_do_dono(self, dono_id: int, termo: str) -> list[Exame]:
        linhas = self._conexao.execute(
            f"SELECT {_COLUNAS} FROM exames WHERE dono_id = ? AND nome LIKE ? ORDER BY nome",
            (dono_id, f"%{termo}%"),
        ).fetchall()
        return [Exame(*linha) for linha in linhas]

    def incluir(self, dono_id: int, nome: str, detalhe: str, nota: str) -> None:
        self._conexao.execute(
            "INSERT INTO exames (dono_id, nome, detalhe, nota) VALUES (?, ?, ?, ?)",
            (dono_id, nome, detalhe, nota),
        )

    def recentes(self, limite: int = 20) -> list[tuple[Exame, str]]:
        """Últimos exames de todos os usuários, com o nome de quem cadastrou."""
        linhas = self._conexao.execute(
            f"SELECT {', '.join('e.' + c.strip() for c in _COLUNAS.split(','))}, u.nome "
            "FROM exames e JOIN usuarios u ON u.id = e.dono_id ORDER BY e.id DESC LIMIT ?",
            (limite,),
        ).fetchall()
        return [(Exame(*linha[:6]), linha[6]) for linha in linhas]
