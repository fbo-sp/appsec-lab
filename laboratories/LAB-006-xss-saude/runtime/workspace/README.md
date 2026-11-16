# Rede Lumina Diagnósticos · Portal do Paciente

Aplicação de **treinamento** (dados fictícios) com uma falha de Cross-Site Scripting (XSS) intencional.

## Como a aplicação está organizada

1. **`controllers/auth_controller.py`**: login e logout; guarda o usuário em `session` e grava um cookie lido pelo front-end.
2. **`controllers/exame_controller.py`**: busca de exames (`/exames?q=...`) e cadastro.
3. **`controllers/painel_controller.py`**: fila de atendimento (`/painel`), só para a equipe interna.
4. **`services/exame_service.py`**: regras de negócio, incluindo a limpeza do texto digitado.
5. **`repositories/`**: consultas ao banco, sempre com parâmetros (`?`).
6. **`templates/`**: páginas HTML montadas pelo Jinja2.

O banco (`/tmp/lumina.db`) é recriado por `database/seed.py` sempre que a aplicação inicia.

## Comandos úteis no terminal

```bash
grep -iE "error|traceback" /tmp/app.log | tail -n 15   # erros da aplicação (o log também traz os acessos)
grep -rn "safe" templates/                              # onde o template desliga a proteção do Jinja2
```

A aplicação recarrega sozinha quando você salva um arquivo `.py` ou um template.
