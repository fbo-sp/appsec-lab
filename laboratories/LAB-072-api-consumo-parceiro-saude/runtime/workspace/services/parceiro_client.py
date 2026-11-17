"""Cliente da API do Rede Atlas Credenciados: faz a chamada HTTP e devolve o JSON da resposta."""

import json
import urllib.error
import urllib.request


class ParceiroIndisponivel(Exception):
    """O parceiro não respondeu ou respondeu com erro."""


class ParceiroClient:
    def __init__(self, url_base: str) -> None:
        self._url_base = url_base

    def consultar(self, referencia: str) -> dict:
        url = f"{self._url_base}/consulta/{referencia}"
        try:
            with urllib.request.urlopen(url, timeout=3) as resposta:
                return json.loads(resposta.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError) as erro:
            raise ParceiroIndisponivel(str(erro)) from erro
