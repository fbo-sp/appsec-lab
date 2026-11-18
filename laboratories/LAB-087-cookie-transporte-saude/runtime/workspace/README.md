# Aliança Médico Conveniado · Cooperativa Médica Aliança (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **proteção da sessão no transporte** (OWASP A02:2021, A04:2025) para você
encontrar e corrigir.

## Como ela está organizada

```
navegador -> (HTTPS no balanceador) -> controllers/ -> services/ -> repositories/ -> banco SQLite
                                           |
                                           +-> templates/  (monta o HTML de resposta)
```

- `config.py` — **as opções do cookie de sessão e os cabeçalhos de segurança.** É aqui que está a falha.
- `app.py` — aplica os cabeçalhos de `Config.CABECALHOS_SEGURANCA` em toda resposta.
- `controllers/auth_controller.py` — o login, que cria o cookie de sessão.

## A feature

Depois do login, o navegador guarda o cookie `session` e o envia em cada pedido: quem tem esse cookie
é você. O cookie sai sem `Secure` (pode viajar por HTTP), sem `HttpOnly` (o JavaScript da página
consegue lê-lo) e sem `SameSite`, e a aplicação não manda o navegador usar sempre HTTPS (HSTS).
