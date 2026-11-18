"""Camada de serviço: a autorização das funções administrativas. É AQUI que mora a falha.

A autenticação diz QUEM é o usuário (ele fez login). A autorização diz O QUE ele pode fazer. A API
administrativa (listar todos os usuários) é uma função que só o papel ``admin`` deveria poder usar.
A falha: este serviço libera a função para qualquer usuário autenticado, sem conferir o papel. Um
usuário comum, logado, chama a API de admin e recebe a lista completa — é falha de autorização em
nível de função (BFLA: Broken Function Level Authorization).
"""


class PermissaoService:
    def pode_administrar(self, papel: str) -> bool:
        """Diz se o papel pode usar as funções administrativas."""
        # Não confere o papel: qualquer usuário autenticado é liberado.
        return True
