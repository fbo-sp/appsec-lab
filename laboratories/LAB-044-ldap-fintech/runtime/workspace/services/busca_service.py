"""Camada de serviço: a busca de pessoas no diretório. É AQUI que mora a falha.

A busca monta um filtro no estilo LDAP a partir do nome digitado e consulta o diretório. A falha: ela
junta o nome CRU no filtro. Como o ``*`` é curinga nos filtros LDAP, buscar por ``*`` vira ``(cn=*)``
e lista o diretório inteiro — é injeção de LDAP. A defesa é ESCAPAR os caracteres especiais do filtro
antes de montá-lo, para que o que o usuário digita seja tratado como texto, não como sintaxe.
"""

from diretorio import buscar


class BuscaService:
    def por_nome(self, nome: str) -> list[dict[str, str]]:
        """Busca no diretório as pessoas cujo cn casa com o nome informado."""
        # Junta o nome cru no filtro: um * digitado vira curinga e lista tudo.
        filtro = f"(cn={nome})"
        return buscar(filtro)
