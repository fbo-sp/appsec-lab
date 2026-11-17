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

- `static/app.js` — o app: o botão **Liberar manobra no disjuntor 7** chama `POST /api/operacoes`; ao abrir um link
  `auroracampo://manobra?alvo=...&detalhe=...` (deep link), chama `POST /api/operacoes/rapida`.
- `controllers/api_controller.py` — a API: login, conta, itens e operações.
- `services/operacao_service.py` — **decide se a operação fica pendente ou é executada. É aqui que está a falha.**

## A falha

O fluxo do botão tem duas etapas: a operação fica pendente e só é executada quando o usuário toca em
**Confirmar** (código de uso único). O caminho do deep link, criado para a campanha "um toque",
executa a operação na hora, sem confirmação. Qualquer link que chegue ao celular dispara a operação.
