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

- `static/app.js` — o app: a aba **Mensagens** busca `GET /api/mensagens/pagina` e mostra a página num WebView.
- `controllers/api_controller.py` — a API: login, conta, itens e mensagens (Aviso de turno).
- `services/mensagem_service.py` — grava e lista as mensagens como vieram.
- `templates/webview_mensagens.html` — **a página da central. É aqui que está a falha.**

## A falha

A página mostra o texto de cada mensagem com o filtro `|safe`, sem codificação de saída e sem política
de conteúdo. Uma mensagem escrita por outro usuário vira HTML dentro do app oficial.
