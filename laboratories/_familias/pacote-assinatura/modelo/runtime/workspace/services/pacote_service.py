"""Camada de serviço: importação dos pacotes de [[pacote_tipo]]. É AQUI que mora a falha.

O [[fornecedor]] envia cada pacote como um arquivo JSON com os campos ``fornecedor``, ``versao``,
``parametros`` e ``assinatura``. A assinatura é um HMAC-SHA256, feito com a chave combinada entre as
duas empresas (Config.CHAVE_FORNECEDOR), sobre o conteúdo canônico do pacote (veja
``conteudo_canonico``). Ela prova que o pacote veio do fornecedor e não foi alterado no caminho.

A falha: ``importar`` aplica os parâmetros sem recalcular e conferir a assinatura. Um pacote alterado
depois de assinado, ou sem assinatura nenhuma, é aceito do mesmo jeito.
"""

import hashlib
import hmac
import json

from repositories.parametro_repository import ParametroRepository

CAMPOS_OBRIGATORIOS = ("fornecedor", "versao", "parametros")


class PacoteInvalido(ValueError):
    """O pacote não pode ser aplicado."""


def conteudo_canonico(pacote: dict) -> bytes:
    """Os bytes que o fornecedor assina: o pacote sem a assinatura, em JSON com chaves ordenadas."""
    sem_assinatura = {chave: valor for chave, valor in pacote.items() if chave != "assinatura"}
    return json.dumps(sem_assinatura, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class PacoteService:
    def __init__(self, repositorio: ParametroRepository, chave_fornecedor: str) -> None:
        self._repositorio = repositorio
        self._chave = chave_fornecedor.encode("utf-8")

    def _ler(self, texto: str) -> dict:
        try:
            pacote = json.loads(texto)
        except json.JSONDecodeError as erro:
            raise PacoteInvalido("o arquivo não é um JSON válido.") from erro
        if not isinstance(pacote, dict) or any(campo not in pacote for campo in CAMPOS_OBRIGATORIOS):
            raise PacoteInvalido("faltam campos obrigatórios no pacote.")
        if not isinstance(pacote["parametros"], dict):
            raise PacoteInvalido("o campo parametros precisa ser um objeto.")
        return pacote

    def importar(self, texto: str) -> dict:
        """Lê o pacote recebido do fornecedor e aplica os parâmetros."""
        pacote = self._ler(texto)
        self._repositorio.substituir(str(pacote["versao"]), str(pacote["fornecedor"]), pacote["parametros"])
        return pacote
