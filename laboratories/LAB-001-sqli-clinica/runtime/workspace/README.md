# Clínica VidaPlena · portal de agendamento

Aplicação de **treinamento** (dados fictícios) com uma falha de SQL Injection intencional.

## Como a busca funciona

1. **`controllers/medicos_controller.py`**: a rota `/medicos` lê o campo `nome` do formulário.
2. **`services/medico_service.py`**: o serviço limpa o termo (espaços e tamanho máximo).
3. **`repositories/medico_repository.py`**: o repositório monta o SQL e consulta o banco.
4. **`models/medico.py`**: cada linha do banco vira um objeto `Medico`.
5. **`templates/medicos.html`**: a página mostra a tabela de resultados.

O banco (`/tmp/clinica.db`) é recriado por `database/seed.py` sempre que a aplicação inicia.

## Comandos úteis no terminal

```bash
tail -n 20 /tmp/app.log      # últimas linhas do log da aplicação
tail -f /tmp/app.log         # acompanha o log em tempo real (Ctrl+C para sair)
```

A aplicação recarrega sozinha quando você salva um arquivo `.py`.
