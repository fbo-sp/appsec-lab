"""Camada de serviço: a leitura de documentos. É AQUI que mora a falha deste laboratório.

O usuário baixa um documento pelo nome. Este serviço monta o caminho juntando a pasta de documentos
com o nome que veio na requisição e abre o arquivo. A falha: ele não confere se o caminho final
continua DENTRO da pasta de documentos. Com um nome como ``../segredo_interno.txt`` (ou um caminho
absoluto), o usuário sai da pasta e lê arquivos que não deveria — é o *path traversal*.
"""

import os


class DocumentoService:
    # Pasta onde ficam os documentos que o usuário pode baixar.
    BASE = "/workspace/documentos"

    def ler(self, nome: str) -> str:
        """Lê o documento de nome ``nome`` dentro da pasta de documentos e devolve o conteúdo."""
        caminho = os.path.join(self.BASE, nome)
        with open(caminho, encoding="utf-8") as arquivo:
            return arquivo.read()
