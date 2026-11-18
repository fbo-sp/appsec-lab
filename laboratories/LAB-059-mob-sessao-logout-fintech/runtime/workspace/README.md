# App Pagomais · Pagomais (ambiente de treinamento)

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

- `controllers/api_controller.py` — a API: login, conta, itens e `POST /api/sair`.
- `repositories/token_repository.py` — os tokens emitidos no login (ativos ou revogados).
- `services/sessao_service.py` — **o logout. É aqui que está a falha.**

## A falha

Ao tocar em Sair, o app esquece o token, mas o servidor não o revoga. Qualquer cópia do token continua
abrindo a conta. A defesa é revogar o token no servidor no logout.
