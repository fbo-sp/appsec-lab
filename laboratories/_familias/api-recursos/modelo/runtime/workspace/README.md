# [[app_nome]] · [[empresa]] (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **consumo irrestrito de recursos** (OWASP API4) para você encontrar e corrigir.

## Como ela está organizada

```
navegador / app -> controllers/ -> services/ -> repositories/ -> banco SQLite
```

- `controllers/api_controller.py` — a API `/api/[[recurso]]`, com os parâmetros `limite` e `pagina`.
  Registra no log o tamanho e o tempo de cada listagem.
- `services/[[recurso_singular_arquivo]]_service.py` — **a paginação.** Usa o `limite` que o cliente
  mandar, sem teto. É aqui que está a falha.
- `repositories/`, `models/`, `database/seed.py` — os [[total]] [[recurso_plural]] fictícios da conta.

## A feature

O app pede 20 [[recurso_plural]] por vez. A API aceita qualquer `limite`: com `limite=100000` o servidor
lê e monta a base inteira numa resposta só, e um número negativo também abre tudo (no SQLite,
`LIMIT -1` é "sem limite"). Num banco de produção, com milhões de linhas, poucas chamadas assim
derrubam o serviço. A defesa é aplicar no servidor um teto de página.
