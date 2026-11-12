# Ambiente local (Docker Desktop)

Executa somente componentes **confiáveis** da 1ª fatia: PostgreSQL, migração, API e worker.
O runtime de laboratórios é o `FakeRuntimeAdapter` (não executa contêineres de aluno). Docker Compose
**não** é fronteira de isolamento para código hostil (docs/07, ADR-002).

## Subir

```powershell
# na raiz do repositório
docker compose -f infrastructure/local/docker-compose.yml up --build -d
docker compose -f infrastructure/local/docker-compose.yml ps        # api deve ficar "healthy"
```

- API: http://127.0.0.1:8000 · Swagger: http://127.0.0.1:8000/api/docs
- PostgreSQL: 127.0.0.1:5432 (usuário `appsec`, senha local `local-dev-only` ou `POSTGRES_PASSWORD`)
- Autenticação de desenvolvimento por cabeçalho: `X-Dev-User: <id>` e `X-Dev-Roles: student|admin`

## Demonstração

```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo-local.ps1
```

Registra o LAB-000, cria a sessão (com replay idempotente), aguarda `READY`, verifica que outro usuário
recebe 404 e encerra até `TERMINATED`.

## Logs, parada e limpeza

```powershell
docker compose -f infrastructure/local/docker-compose.yml logs -f worker   # logs JSON
docker compose -f infrastructure/local/docker-compose.yml down             # para (mantém dados)
docker compose -f infrastructure/local/docker-compose.yml down -v          # para e APAGA o banco local
```

Alternativa sem Docker (Linux/macOS): `scripts/dev-db.sh start` + `scripts/demo-slice.sh`.
