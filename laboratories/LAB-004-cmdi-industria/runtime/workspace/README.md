# Ferrara Metais · Portal de Manutenção

Aplicação de **treinamento** (dados fictícios, CLPs simulados) com uma falha de Command Injection intencional.

## Como o teste de comunicação funciona

1. **`controllers/diagnostico_controller.py`**: a rota `/diagnostico` lê o campo `endereco` do formulário.
2. **`services/diagnostico_service.py`**: o serviço monta o comando do teste.
3. **`infra/executor_comandos.py`**: executa o programa do sistema operacional e devolve a saída.
4. **`repositories/equipamento_repository.py`**: lê o inventário de CLPs (`/opt/planta/equipamentos.csv`).

O programa `diag-clp` (em `/usr/local/bin`) simula o teste Modbus/TCP: ele não acessa nenhuma rede.

## Comandos úteis no terminal

```bash
tail -n 20 /tmp/app.log      # últimas linhas do log da aplicação (inclui cada comando executado)
diag-clp 10.20.1.15          # o mesmo teste que a página faz
```

A aplicação recarrega sozinha quando você salva um arquivo `.py`.
