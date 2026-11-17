# App Aurora Campo · Aurora Energia (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de segurança para você encontrar e corrigir.

## Como ela está organizada

```
app no celular (templates/app.html + static/app.js)
        |
        v  chama a API como um app Android/iOS faria
controllers/api_controller.py -> services/ -> repositories/ -> banco SQLite
```

O app que aparece na moldura de celular da aba **Aplicação** é um cliente mobile **simulado**: não há
emulador, mas ele conversa com a API do servidor do mesmo jeito que um app nativo.

## Arquivos principais

- `cliente/config.json` — a configuração empacotada no app; `token_na_url` faz o app mandar o token na URL.
- `static/app.js` — o app: manda o token em `Authorization: Bearer` e, com `token_na_url`, também em `?token=`.
- `controllers/api_controller.py` — a API: login, conta e itens.
- `services/identidade_service.py` — **identifica o usuário do pedido. Aceita o token da URL: é aqui que está a falha do servidor.**

## A falha

O token de sessão viaja na URL (`?token=...`) e o servidor aceita. A URL completa fica gravada no log
de acesso, em proxies e em ferramentas de monitoramento; quem lê esses logs reaproveita o token.
