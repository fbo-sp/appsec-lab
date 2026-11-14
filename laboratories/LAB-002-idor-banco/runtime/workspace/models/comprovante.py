"""Modelo de domínio: o comprovante de um PIX enviado."""

from dataclasses import dataclass


@dataclass
class Comprovante:
    id: int
    cliente_id: int  # dono do comprovante: o cliente que pagou
    data_hora: str
    valor_centavos: int
    recebedor_nome: str
    recebedor_documento: str
    chave_pix: str
    id_transacao: str
    # Dados do pagador, vindos da tabela de clientes.
    pagador_nome: str
    pagador_documento: str
    pagador_agencia: str
    pagador_conta: str

    @property
    def valor_formatado(self) -> str:
        reais, centavos = divmod(self.valor_centavos, 100)
        return f"R$ {reais:,}".replace(",", ".") + f",{centavos:02d}"

    def para_dicionario(self) -> dict[str, object]:
        return {
            "id": self.id,
            "data_hora": self.data_hora,
            "valor": self.valor_formatado,
            "pagador": {
                "cliente_id": self.cliente_id,
                "nome": self.pagador_nome,
                "documento": self.pagador_documento,
                "agencia": self.pagador_agencia,
                "conta": self.pagador_conta,
            },
            "recebedor": {
                "nome": self.recebedor_nome,
                "documento": self.recebedor_documento,
                "chave_pix": self.chave_pix,
            },
            "id_transacao": self.id_transacao,
        }
