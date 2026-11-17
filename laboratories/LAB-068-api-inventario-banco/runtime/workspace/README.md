# Cobalto Online · Banco Cobalto (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **gestão de inventário de API** (OWASP API9) para você encontrar e corrigir.

## Como ela está organizada

```
navegador / app -> controllers/ -> services/ -> repositories/ -> banco SQLite
                       |
                       +-> templates/  (monta o HTML de resposta)
```

- `app.py` — registra as rotas. Repare que **duas versões** da API estão registradas.
- `controllers/api_v2_controller.py` — a API atual (v2), documentada em `/api/docs`. Confere o dono.
- `controllers/api_v1_controller.py` — a API legada (v1). **Saiu da documentação, mas continua no ar.**
  É aqui que está a falha.
- `services/documento_service.py` — a regra do dono (só a v2 usa).
- `repositories/documento_repository.py`, `models/documento.py`, `database/seed.py` — os comprovantes.

## A feature

Cada cliente vê os próprios comprovantes. A v2 da API devolve um documento só para o dono. A v1,
de 2022, buscava direto pelo id; quando a v2 entrou, a v1 foi apagada da documentação e ninguém
a desligou. Quem conhece a rota antiga troca `v2` por `v1` e lê documentos de qualquer cliente. A
defesa é manter o inventário de todas as versões publicadas e aposentar (ou corrigir) as antigas.
