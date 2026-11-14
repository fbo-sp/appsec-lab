#!/usr/local/bin/python
"""diag-clp: teste de comunicação Modbus/TCP com CLPs da planta (SIMULADO para o laboratório LAB-004).

Não abre conexões de rede: responde a partir do inventário fictício em /opt/planta/equipamentos.csv.
"""

import csv
import ipaddress
import sys

INVENTARIO = "/opt/planta/equipamentos.csv"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: diag-clp <endereço IPv4 do CLP>")
        return 2
    endereco = argv[1].strip()
    try:
        ipaddress.IPv4Address(endereco)
    except ValueError:
        print(f"diag-clp: endereço inválido: {endereco!r}")
        return 2
    with open(INVENTARIO, encoding="utf-8") as arquivo:
        equipamentos = {linha["endereco"]: linha for linha in csv.DictReader(arquivo, delimiter=";")}
    print(f"Testando comunicação Modbus/TCP com {endereco}:502 ...")
    clp = equipamentos.get(endereco)
    if clp is None:
        print("sem resposta (timeout após 3 tentativas)")
        return 1
    print(f"resposta de {clp['nome']} ({clp['linha']})")
    print(f"tempo={clp['latencia_ms']} ms  status=OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
