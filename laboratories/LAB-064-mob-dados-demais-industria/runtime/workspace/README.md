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

- `controllers/api_controller.py` — a API: login, conta, itens e `GET /api/perfil`.
- `repositories/conta_repository.py` — `perfil_completo` lê o registro inteiro da conta (uso interno).
- `services/perfil_service.py` — **o que a API entrega para a tela Perfil. É aqui que está a falha.**

## A falha

A tela Perfil mostra nome e resumo, mas a API devolve também documento e dado pessoal. Tudo o que a API
devolve chega ao aparelho. A defesa é a minimização: devolver só os campos que a tela usa.
