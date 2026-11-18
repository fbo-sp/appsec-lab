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

- `static/regras.js` — as regras do app: qual plano ele considera para a conta e a "verificação de integridade" que ele mesmo faz.
- `static/app.js` — o app: mostra o recurso **Relatório de ativos** só no plano avançado (habilitação de supervisor), pede o selo de integridade e chama a API.
- `controllers/api_controller.py` — a API: login, conta, itens, selo de integridade e recurso.
- `services/atestacao_service.py` — **simula** o serviço de integridade da loja (Play Integrity / App Attest). Sem falha.
- `services/recurso_service.py` — **decide se a conta pode usar o recurso. Confia no plano e na integridade que o app informa: é aqui que está a falha.**

## A falha

O servidor libera o recurso do plano avançado porque o app diz que a conta é desse plano e que o app
está íntegro. O app roda no celular do usuário e pode ser modificado e reempacotado: um app
modificado diz o que quiser. O servidor precisa decidir o plano pelo cadastro e conferir o selo
assinado pela loja.
