# Portal de Pagamentos · Pagomais (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de segurança na **API GraphQL de pedidos** para você encontrar e corrigir.

## Como ela está organizada

```
navegador/cliente -> controllers/ -> services/ -> repositories/ -> banco SQLite
                         |
                         +-> templates/  (monta o HTML do painel)
```

- `controllers/painel_controller.py` — expõe a API `POST /graphql` e chama o resolver.
- `services/pedido_service.py` — **o resolver do pedido**. Recebe o id do usuário logado e o id do
  pedido pedido na query. **É aqui que está a falha.**
- `repositories/pedido_repository.py`, `models/pedido.py`, `database/seed.py` — os pedidos e seus donos.
- `controllers/auth_controller.py`, `services/auth_service.py` — o login (não é o foco).

## A feature

O usuário entra e consulta seus pedidos pela API `POST /graphql`, com um corpo JSON como
`{"query": "{ pedido(id: 1) { descricao valor } }", "variables": {"id": 1}}`. (Para o laboratório
ficar direto, a API é um GraphQL **simplificado**: só a operação `pedido` existe e o id vem de
`variables.id`.)

O problema: o resolver devolve o pedido **só pelo id**, sem conferir se aquele pedido é do usuário
logado. Então, logado como um usuário, dá para pedir o pedido de **qualquer outro** só trocando o id
— é **BOLA** (Broken Object Level Authorization), a autorização por objeto quebrada. A defesa é o
resolver conferir que o objeto pertence ao dono logado antes de devolvê-lo. Estar autenticado não
basta: cada objeto tem que checar o dono.
