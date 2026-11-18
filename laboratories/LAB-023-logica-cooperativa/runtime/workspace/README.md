# Resgate de Investimento · Cooperativa Credimova (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **lógica de negócio** para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — recebe o valor do formulário de resgate e chama o serviço.
- `services/resgate_service.py` — **a regra de negócio do resgate**. É aqui que se decide se o valor
  pedido é válido. É aqui que está a falha.
- `services/auth_service.py` + `controllers/auth_controller.py` — login (não é o foco; as senhas já
  usam hash forte).
- `repositories/conta_repository.py`, `models/conta.py`, `database/seed.py` — a conta e o saldo.

## A feature

O usuário entra e vê o próprio saldo. Ele pode **resgatar** um valor desse saldo. A pergunta de
negócio é simples: o valor pedido faz sentido? Se o serviço aceitar qualquer valor que chega do
formulário — negativo, zero ou acima do saldo —, o usuário resgata o que não deveria.
