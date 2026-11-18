# [[empresa]] · [[app_nome]]

Aplicação de **treinamento** (dados fictícios) com uma falha de atribuição em massa (*mass assignment*) intencional.

## Como a aplicação está organizada

1. **`controllers/auth_controller.py`**: login e logout; o usuário logado é lido do banco a cada requisição.
2. **`controllers/perfil_controller.py`**: tela **Meu perfil** (`/perfil`) e a API que ela usa (`GET` e `PATCH /api/perfil`).
3. **`controllers/area_controller.py`**: [[area_priv_titulo]] (`/[[rota_priv]]`), só para o perfil `[[perfil_priv]]`.
4. **`services/perfil_service.py`**: regras de negócio da atualização do perfil.
5. **`repositories/usuario_repository.py`**: consultas ao banco, sempre com parâmetros (`?`).
6. **`templates/`**: páginas HTML montadas pelo Jinja2.

O banco (`/tmp/[[banco]].db`) é recriado por `database/seed.py` sempre que a aplicação inicia, inclusive quando você salva um arquivo `.py`.

## Comandos úteis no terminal

```bash
grep "Perfil atualizado" /tmp/app.log                    # quais campos cada PATCH gravou
grep -iE "error|traceback" /tmp/app.log | tail -n 15     # erros da aplicação (o log também traz os acessos)
```
