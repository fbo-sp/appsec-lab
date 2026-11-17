"""Camada de serviço: importar um documento a partir da URL informada pelo sistema parceiro.

O parceiro manda a URL do documento (no Serviço de Documentos interno) e a [[app_nome]] busca o
conteúdo para mostrar a prévia ao analista. A busca acontece **no servidor**: é o servidor da
aplicação que abre a URL, não o navegador do analista.
"""

import urllib.request


class ImportadorService:
    def importar(self, url: str) -> str:
        """Busca o documento na URL informada e devolve o conteúdo para a prévia."""
        if not url:
            raise ValueError("Informe a URL do documento.")
        # Abre a URL que veio no formulário e devolve o conteúdo buscado.
        with urllib.request.urlopen(url, timeout=3) as resposta:  # noqa: S310
            return resposta.read().decode("utf-8", "replace")[:4000]
