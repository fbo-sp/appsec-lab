# Banco Vértice Digital · Internet Banking

Aplicação de **treinamento** (dados fictícios) com uma falha de controle de acesso intencional.

## Como a consulta de comprovantes funciona

1. **`controllers/auth_controller.py`**: login; o id do cliente logado fica em `session["cliente_id"]`.
2. **`controllers/comprovantes_controller.py`**: rotas `/comprovantes`, `/comprovantes/<número>` e `/api/comprovantes/<número>`.
3. **`services/comprovante_service.py`**: regras de negócio dos comprovantes.
4. **`repositories/comprovante_repository.py`**: consultas ao banco.
5. **`models/comprovante.py`**: cada linha do banco vira um objeto `Comprovante`.

O banco (`/tmp/banco.db`) é recriado por `database/seed.py` sempre que a aplicação inicia.

## Comandos úteis no terminal

```bash
tail -n 20 /tmp/app.log      # últimas linhas do log da aplicação
curl -s http://127.0.0.1:8080/api/comprovantes/10458 -b /tmp/cookies.txt   # API com o cookie salvo
```

A aplicação recarrega sozinha quando você salva um arquivo `.py`.
