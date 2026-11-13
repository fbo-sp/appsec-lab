# Orbe Cartões · Portal do cliente

Aplicação de **treinamento** (dados fictícios) com uma falha intencional na validação de tokens JWT.

## Como a autenticação funciona

1. **`routes/`**: define as rotas `/api/login`, `/api/cartoes/meu` e `/api/admin/...`.
2. **`middlewares/autenticacao.js`**: `autenticar` lê o token do cabeçalho `Authorization: Bearer <token>`; `exigirPerfil` confere o perfil.
3. **`services/token.service.js`**: emite o token no login e lê o token de cada requisição.
4. **`controllers/`** e **`services/`**: regras de negócio de cartões e do painel do gerente.
5. **`repositories/`**: dados em memória, recriados por `data/seed.js` a cada início.

## Comandos úteis no terminal

```bash
tail -n 20 /tmp/app.log      # últimas linhas do log da aplicação
curl -s -X POST http://127.0.0.1:8080/api/login -H "Content-Type: application/json" \
  -d '{"email":"larissa.mendes@clientes.orbe.example","senha":"Larissa@2026"}'
```

A aplicação reinicia sozinha quando você salva um arquivo `.js` (`node --watch`).
