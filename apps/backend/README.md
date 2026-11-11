# Backend — plano de controle (monólito modular)

| Módulo | Responsabilidade | Docs |
|---|---|---|
| `app/catalog` | Registro de releases imutáveis a partir de manifestos validados | 11, 12, FR-010–012 |
| `app/sessions` | Máquina de estados, criação idempotente, consulta, encerramento | 08, FR-020–026 |
| `app/runtime` | `RuntimePort` + `FakeRuntimeAdapter` (único adapter por enquanto) | 08 §7, 09 §4 |
| `app/jobs` | Fila transacional no PostgreSQL com lease | ADR-007 |
| `app/workers` | Provisioner (PROVISION/TERMINATE) e reconciliador (TTL, órfãos) | 08 §5–6 |
| `app/audit` | Eventos de auditoria na mesma transação | NFR-010 |
| `app/identity` | `Principal`, papéis; autenticação **de desenvolvimento** por cabeçalho | FR-001–003 (parcial) |
| `app/shared` | Erros (`13 §5`), logs JSON, correlação, relógio | FR-053 |

Somente `app/runtime` conhece adapters concretos; o restante usa `RuntimePort`.

```bash
export DATABASE_URL=$(../../scripts/dev-db.sh url) APP_ENV=local AUTH_MODE=dev
uv run alembic upgrade head
uv run uvicorn --factory app.main:app_factory --port 8000   # API (docs em /api/docs)
uv run python -m app.workers.run                            # worker (um único processo com o fake)
```

Autenticação de desenvolvimento: cabeçalhos `X-Dev-User: <id>` e `X-Dev-Roles: student|instructor|admin`.
Só é aceita com `APP_ENV=local|test`; a aplicação se recusa a iniciar nesse modo em outros ambientes.
