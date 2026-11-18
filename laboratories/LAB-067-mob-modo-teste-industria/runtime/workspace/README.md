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

- `controllers/api_controller.py` — a API: login, conta e itens. Todas as rotas perguntam ao serviço de identidade quem é o usuário.
- `services/identidade_service.py` — **identifica o usuário do pedido. É aqui que está a falha.**

## A falha

Ficou no código um atalho de homologação: com o cabeçalho `X-Debug: 1`, a API trata o pedido como da
conta 1, sem login. A defesa é tirar o atalho do build de produção: só o token do login identifica.
