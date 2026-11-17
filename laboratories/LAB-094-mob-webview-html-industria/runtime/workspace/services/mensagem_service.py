"""Camada de serviço: a central de mensagens (Avisos de turno).

Qualquer usuário do app pode escrever para outro (Aviso de turno). O texto é guardado como veio:
quem decide como ele aparece na tela é a página da central, templates/webview_mensagens.html, que o
app mostra num WebView. A falha deste laboratório está nessa página.
"""

from models.mensagem import Mensagem
from repositories.conta_repository import ContaRepository
from repositories.mensagem_repository import MensagemRepository

TAMANHO_MAXIMO = 500


class MensagemInvalida(ValueError):
    """A mensagem não pode ser enviada."""


class MensagemService:
    def __init__(self, mensagens: MensagemRepository, contas: ContaRepository) -> None:
        self._mensagens = mensagens
        self._contas = contas

    def enviar(self, autor_id: int, para_login: str, texto: str) -> None:
        destino = self._contas.buscar_por_login(para_login.strip().lower())
        if destino is None:
            raise MensagemInvalida("destinatário não encontrado")
        if not texto.strip() or len(texto) > TAMANHO_MAXIMO:
            raise MensagemInvalida("mensagem vazia ou longa demais")
        autor = self._contas.buscar(autor_id)
        self._mensagens.gravar(destino[0].id, autor.nome, texto)

    def da_conta(self, conta_id: int) -> list[Mensagem]:
        return self._mensagens.da_conta(conta_id)
