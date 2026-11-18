# Portal do Corretor Maré Alta · Seguradora Maré Alta (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **registro e monitoramento** (OWASP A09) para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/auth_controller.py` — o formulário de login; passa o IP de quem tenta entrar.
- `services/auth_service.py` — **o login e a auditoria.** Só registra o login que deu certo. É aqui
  que está a falha.
- `repositories/auditoria_repository.py` — grava e lê a trilha de auditoria (tabela `auditoria`).
- `database/seed.py` — as contas fictícias.

## A feature

Cada evento de segurança vai para a trilha de auditoria, que o time de monitoramento usa para
detectar e investigar ataques. Hoje, só o login bem-sucedido é registrado: centenas de senhas
erradas numa conta não deixam rastro nenhum. A defesa é registrar sucesso e falha, com login, IP e
hora, e nunca a senha digitada.
