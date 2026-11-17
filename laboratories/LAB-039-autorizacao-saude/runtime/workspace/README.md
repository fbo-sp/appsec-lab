# Console Interno · Hospital Santa Clara (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **autorização em nível de função** (BFLA) para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — a área logada e a **API administrativa** `/api/admin/usuarios`,
  que lista todos os usuários.
- `services/permissao_service.py` — **a autorização**. Decide se o papel do usuário pode usar as
  funções administrativas. É aqui que está a falha.
- `services/auth_service.py` — login (não é o foco; as senhas já usam hash forte). O papel do usuário
  (`comum` ou `admin`) vai para a sessão no login.
- `repositories/conta_repository.py`, `models/conta.py`, `database/seed.py` — as contas e os papéis.

## A feature

Depois do login, o usuário tem um **papel**: `comum` ou `admin`. A API `/api/admin/usuarios` lista
todos os usuários e deveria ser restrita ao papel `admin`. O problema é que a autorização libera a
função para **qualquer usuário autenticado**, sem conferir o papel. Assim, um usuário comum logado
chama a API administrativa e recebe a lista completa. A defesa é conferir o papel antes de executar a
função: só `admin` pode.
