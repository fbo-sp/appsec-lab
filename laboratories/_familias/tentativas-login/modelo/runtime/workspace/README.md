# [[app_nome]] · [[empresa]] (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de segurança no **login** para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/auth_controller.py` — recebe usuário e senha do formulário e chama o serviço de login.
- `services/auth_service.py` — **a autenticação**. Confere a senha (com hash forte) e devolve a conta.
  É aqui que falta decidir **quantas tentativas seguidas** um usuário pode ter. É aqui que está a falha.
- `repositories/conta_repository.py`, `models/conta.py`, `database/seed.py` — a conta e as credenciais.
- `controllers/painel_controller.py` — a área logada (não é o foco).

## A feature

O usuário entra com usuário e senha. As senhas já usam hash forte, então o problema **não** é o
armazenamento. O problema é que o login aceita **tentativas ilimitadas**: um atacante pode testar
senha após senha (força bruta) sem nada no caminho para detê-lo. A defesa é **limitar as tentativas
por usuário** e bloquear quando passar do limite.
