"""Camada de serviço: gera o relatório do mês informado (fonte de um erro possível)."""


class RelatorioService:
    def gerar(self, mes: str) -> int:
        """Devolve o número do mês do relatório. Lança se o mês não for um número válido."""
        numero = int(mes)  # ValueError se 'mes' não for numérico
        if not 1 <= numero <= 12:
            raise ValueError("mês fora do intervalo")
        return numero
