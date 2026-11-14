"""Camada de acesso a dados: lê o inventário de CLPs da planta."""

import csv

from models.equipamento import Equipamento


class EquipamentoRepository:
    def __init__(self, caminho_inventario: str) -> None:
        self._caminho = caminho_inventario

    def listar(self) -> list[Equipamento]:
        with open(self._caminho, encoding="utf-8") as arquivo:
            return [
                Equipamento(linha["endereco"], linha["nome"], linha["linha"])
                for linha in csv.DictReader(arquivo, delimiter=";")
            ]
