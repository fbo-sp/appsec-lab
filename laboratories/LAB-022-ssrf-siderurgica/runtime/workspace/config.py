"""Configuração do Portal de Engenharia da Siderúrgica Pindorama (aplicação de TREINAMENTO).

Todos os valores são fictícios. A aplicação sobe junto com dois serviços internos SIMULADOS
(veja interno/servicos.py), só em loopback, para o importador ter o que buscar.
"""


class Config:
    # Chave de sessão do laboratório (valor fictício, não é segredo real).
    SECRET_KEY = "cecyber-lab-lab-022-ssrf-sessao-ficticia"

    # Serviços internos simulados (sobem com a aplicação, só em loopback):
    #   127.0.0.1:8090 -> Serviço de Documentos (destino LEGÍTIMO do importador)
    #   127.0.0.1:9000 -> Console de Infraestrutura (uso interno; guarda credenciais)
    SERVICO_DOCUMENTOS = "http://127.0.0.1:8090"
    CONSOLE_INFRA = "http://127.0.0.1:9000"
