# App Lumen Saúde · Clínica Lumen (ambiente de treinamento)

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

- `controllers/api_controller.py` — a API: `POST /api/login`, `GET /api/conta` e `GET /api/itens`.
- `dispositivo/sessao_local.py` — **o que o app grava no aparelho depois do login. É aqui que está a falha.**
- `ver_aparelho.py` — mostra o que está gravado no aparelho simulado (`python3 ver_aparelho.py`).

## A falha

Depois do login, o app grava nas preferências do aparelho o login, o token **e a senha em texto puro**.
Quem copia os arquivos do app (perícia, backup, malware, aparelho com root) lê a senha. A defesa é
guardar só o necessário para manter a sessão (o token) e nunca a senha.
