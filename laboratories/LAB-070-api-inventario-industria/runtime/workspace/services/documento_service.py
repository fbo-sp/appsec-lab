"""Camada de serviço: o acesso aos faturas com a regra do dono (usada pela v2)."""

from models.documento import Documento
from repositories.documento_repository import DocumentoRepository


class DocumentoService:
    def __init__(self, repositorio: DocumentoRepository) -> None:
        self._repositorio = repositorio

    def buscar_do_dono(self, doc_id: int, conta_id: int) -> Documento | None:
        """Devolve o documento só quando ele pertence à conta logada."""
        documento = self._repositorio.buscar(doc_id)
        if documento is None or documento.conta_id != conta_id:
            return None
        return documento
