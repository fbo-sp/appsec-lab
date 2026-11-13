"""Configurações da aplicação."""


class Config:
    ARQUIVO_LOG = "/tmp/app.log"
    # Inventário FICTÍCIO de CLPs da planta, mantido pela engenharia de automação.
    INVENTARIO_CLPS = "/opt/planta/equipamentos.csv"
    # Tempo máximo, em segundos, de cada teste de comunicação.
    TEMPO_LIMITE_DIAGNOSTICO = 10
