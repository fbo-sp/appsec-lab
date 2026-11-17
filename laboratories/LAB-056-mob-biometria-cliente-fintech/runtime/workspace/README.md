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

- `controllers/api_controller.py` — a API: login, conta, itens, `POST /api/biometria/prova` e `POST /api/acao`.
- `repositories/prova_repository.py` — as provas de biometria (no lab, fazem o papel do chip seguro).
- `services/acao_service.py` — **a operação sensível. É aqui que está a falha.**

## A falha

O app pede a digital antes da operação, mas a API executa sem conferir a prova da biometria. Quem tem
o token de uma sessão aberta chama `POST /api/acao` direto e pula a digital. A defesa é o servidor
exigir uma prova válida, recente e da mesma conta.
