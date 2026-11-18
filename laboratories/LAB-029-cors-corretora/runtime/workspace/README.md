# Portal do Investidor · Corretora Montara (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **CORS** (compartilhamento de recursos entre origens) para você encontrar e
corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — a área logada e a **API** `/api/perfil`, que devolve o perfil
  do usuário em JSON (a própria página consome essa API por `fetch`).
- `services/cors_service.py` — **a configuração de CORS**. Decide quais origens (sites) podem ler a
  resposta da API pelo navegador. É aqui que está a falha.
- `services/auth_service.py` — login (não é o foco; as senhas já usam hash forte).
- `repositories/conta_repository.py`, `models/conta.py`, `database/seed.py` — a conta e as credenciais.

## A feature

A página carrega o perfil do usuário chamando `/api/perfil`. Para que o navegador deixe uma página de
**outra origem** ler essa resposta, a API precisa dizer, por cabeçalhos CORS, qual origem está
liberada. O problema é que a API **reflete de volta qualquer origem** que chegar na requisição, e
ainda libera o envio de credenciais. Assim, um site malicioso que a vítima visite consegue ler, pelo
navegador dela, os dados da API autenticada. A defesa é liberar só origens **confiáveis**, de uma
lista conhecida.
