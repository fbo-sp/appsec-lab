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

- `cliente/config.json` — a configuração **empacotada no app** (vai dentro do APK/IPA). Tem a chave de API.
- `controllers/api_controller.py` — a API: `POST /api/login`, `GET /api/conta` e `GET /api/itens?conta=N`.
- `services/acesso_service.py` — **decide se o pedido pode ler a lista da conta. É aqui que está a falha.**

## A falha

O servidor libera a lista de qualquer conta para quem mandar a chave do app no cabeçalho `X-Api-Key`.
Como o pacote do app é público, a chave não é segredo: quem a extrai lê a lista de qualquer usuário,
sem login. A defesa é o servidor exigir o **token do usuário** (emitido no login) e conferir que a
conta pedida é a dele.
