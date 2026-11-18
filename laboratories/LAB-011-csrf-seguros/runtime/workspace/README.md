# Vínculo Seguros · Portal do Segurado

Aplicação de **treinamento** (dados fictícios) com uma falha de Cross-Site Request Forgery (CSRF) intencional.

## Como a aplicação está organizada

1. **`controllers/auth_controller.py`**: login e logout; o login fica no cookie de sessão do Flask.
2. **`controllers/indenizacao_controller.py`**: tela **Conta para indenização** (`GET /conta-indenizacao`) e a alteração (`POST /conta-indenizacao`).
3. **`services/indenizacao_service.py`**: regras da alteração e o registro no histórico e no log.
4. **`repositories/`**: consultas ao banco, sempre com parâmetros (`?`).
5. **`templates/`**: páginas HTML montadas pelo Jinja2.
6. **`config.py`**: configurações, inclusive o atributo SameSite do cookie de sessão.

O banco (`/tmp/vinculo.db`) é recriado por `database/seed.py` sempre que a aplicação inicia, inclusive quando você salva um arquivo `.py`.

A página fictícia do atacante fica fora do workspace, em `/opt/atacante/index.html` (só leitura).

## Comandos úteis no terminal

```bash
grep "Destino alterado" /tmp/app.log                     # cada alteração, com a origem informada pelo navegador
grep -iE "error|traceback" /tmp/app.log | tail -n 15     # erros da aplicação (o log também traz os acessos)
cat /opt/atacante/index.html                             # o código da página do atacante
```
