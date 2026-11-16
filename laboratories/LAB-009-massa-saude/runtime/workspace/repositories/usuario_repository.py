"""Camada de repositório: consultas da tabela de usuários."""

import sqlite3

from models.usuario import Usuario

_CAMPOS = "id, login, nome, email, telefone, perfil, plano"

# Colunas que existem na tabela e podem aparecer num UPDATE. Conferir o nome da coluna aqui evita
# SQL injection pelo nome do campo, mas NÃO diz quem pode alterar o quê: isso é regra de negócio.
COLUNAS_ATUALIZAVEIS = ("login", "nome", "email", "telefone", "perfil", "plano", "senha_hash")


class UsuarioRepository:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def buscar_por_login(self, login: str) -> tuple[Usuario, str] | None:
        """Retorna o usuário e o hash da senha, ou None."""
        linha = self._conexao.execute(
            f"SELECT {_CAMPOS}, senha_hash FROM usuarios WHERE login = ?", (login,)
        ).fetchone()
        if linha is None:
            return None
        return Usuario(*linha[:-1]), linha[-1]

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        linha = self._conexao.execute(f"SELECT {_CAMPOS} FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        return Usuario(*linha) if linha else None

    def listar_todos(self) -> list[Usuario]:
        return [Usuario(*linha) for linha in self._conexao.execute(f"SELECT {_CAMPOS} FROM usuarios ORDER BY id")]

    def atualizar(self, usuario_id: int, dados: dict) -> None:
        """Grava no banco cada campo de ``dados`` que for uma coluna conhecida da tabela."""
        colunas = [coluna for coluna in dados if coluna in COLUNAS_ATUALIZAVEIS]
        if not colunas:
            return
        atribuicoes = ", ".join(f"{coluna} = ?" for coluna in colunas)
        valores = [dados[coluna] for coluna in colunas]
        self._conexao.execute(f"UPDATE usuarios SET {atribuicoes} WHERE id = ?", (*valores, usuario_id))

    def buscar_parametro(self, nome: str) -> str | None:
        linha = self._conexao.execute("SELECT valor FROM parametros WHERE nome = ?", (nome,)).fetchone()
        return linha[0] if linha else None
