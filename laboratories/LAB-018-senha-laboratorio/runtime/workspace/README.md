# Laboratórios Helios · Portal do Paciente

Aplicação de **treinamento** (dados fictícios) com uma falha intencional no **armazenamento de senhas**.

As contas foram importadas do sistema legado **"Agenda Saúde"**, e o resumo (hash) de cada senha
foi mantido exatamente como aquele sistema guardava.

## Como a aplicação está organizada

1. **`controllers/auth_controller.py`**: login e logout; o login fica no cookie de sessão do Flask.
2. **`controllers/painel_controller.py`**: a área logada (`GET /painel`), que mostra o formato em que a sua senha está guardada.
3. **`services/auth_service.py`**: a regra de autenticação — **é aqui que a senha digitada é resumida e comparada com o banco** (o ponto da falha).
4. **`repositories/usuario_repository.py`**: consultas ao banco, sempre com parâmetros (`?`).
5. **`templates/`**: páginas HTML montadas pelo Jinja2.
6. **`config.py`**: configurações da aplicação.

O banco (`/tmp/helios.db`) é recriado por `database/seed.py` sempre que a aplicação inicia, inclusive
quando você salva um arquivo `.py`. Por isso, ao corrigir e salvar, as contas voltam ao formato legado e
só são atualizadas quando cada usuário entra de novo.

## Comandos úteis no terminal

```bash
# Ver login e hash de senha de cada conta (o hash é o que está guardado no banco):
python -c "import sqlite3; [print(l) for l in sqlite3.connect('/tmp/helios.db').execute('SELECT login, senha_hash FROM usuarios')]"

# Calcular o resumo MD5 de um texto (para confirmar o formato legado):
python -c "import hashlib; print(hashlib.md5('Trocar@123'.encode()).hexdigest())"

# Erros da aplicação depois de salvar (o log também traz os acessos GET /painel 200):
grep -iE "error|traceback" /tmp/app.log | tail -n 15
```
