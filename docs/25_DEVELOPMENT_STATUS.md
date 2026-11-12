# 25. Status de Desenvolvimento

> **Leia antes de qualquer nova sessão de IA:** este arquivo, `24_IMPLEMENTATION_BACKLOG.md`, `22_PROJECT_INITIAL_ASSESSMENT.md` e `docs/ADR/`. Não declare tarefa concluída sem evidência verificável (comando + resultado).

| Campo | Valor |
|---|---|
| Atualizado em | 2026-11-11 |
| Fase atual | **F1 — Motor mínimo (1ª fatia)** concluída tecnicamente; F0 aprovada pelo PO (2026-11-11) |
| Branch | `claude/project-thread-arhml7` |
| Última entrega concluída | M1 — manifesto → registro → sessão → runtime fake → estado → encerramento/limpeza |

## 1. Funcionalidades implementadas (com escopo real)

| Item | O que funciona | O que **não** está validado |
|---|---|---|
| IMP-101 Estrutura | Workspace uv (`packages/contracts`, `apps/backend`), ruff, mypy strict, pytest, scripts | — |
| IMP-102/103 Manifesto | Modelo `AppSecLab v1alpha1`, JSON Schema exportado, validação estrutural e semântica (ADR-006) | Regra 6 de `11 §3` (validatorRef existir no registro protegido) |
| IMP-104 API base | FastAPI, envelope de erro `13 §5`, `X-Request-Id`, logs JSON com redaction, `/healthz` | OpenAPI formal (IMP-201) |
| IMP-105 Persistência | PostgreSQL + Alembic `0001_engine_core` (upgrade/downgrade testados) | Papéis de BD de menor privilégio; retenção |
| IMP-106 Catálogo | `POST /api/v1/admin/lab-releases` (JSON/YAML, idempotente por digest, imutável), `GET /api/v1/labs`, `GET /api/v1/labs/{id}/releases/{v}` sem dados protegidos | Ciclo draft/retired (IMP-208); filtro por atribuição (IMP-204) |
| IMP-107 Estados | Tabela explícita de transições com correções G-03; `409`/exceção em inválidas; optimistic locking | — |
| IMP-108 Runtime | `RuntimePort` consolidado + `FakeRuntimeAdapter` com injeção de falhas + suíte de contrato | **Nenhum isolamento real**; nenhum contêiner executado |
| IMP-109 Criação | `POST /api/v1/sessions` com `Idempotency-Key`, fingerprint, 1 sessão ativa por usuário+release | Quotas (IMP-205) e atribuição (IMP-204) |
| IMP-110 Worker | Fila PostgreSQL com `SKIP LOCKED`, lease, backoff, dead; provisionamento persiste estado antes do efeito | Métricas OTel (IMP-207) |
| IMP-111 Consulta/encerramento | `GET`/`DELETE /api/v1/sessions/{id}` com ownership (`404` para não-donos, admin auditado); `TERMINATED` só após confirmar ausência | Revogação de gateway (não existe gateway) |
| IMP-112 Reconciliador | TTL → `EXPIRED` → limpeza; órfãos removidos; jobs TERMINATE mortos re-enfileirados | SLA de cleanup (NFR-007 indefinido) |
| IMP-113 Auditoria | `audit_events` na mesma transação, ordem total por `seq` | Imutabilidade por permissão de BD |
| IMP-114 CI | `.github/workflows/ci.yml` (ruff, mypy, validação do LAB-000, pytest com PostgreSQL 16); `main` criada no baseline `aad8812` | Executado no PR #1: job `backend` verde (run 43128706201) |

Laboratório usado: `laboratories/LAB-000-hello-benign` — **benigno, sem vulnerabilidade**. O digest de imagem é uma fixture de teste (não existe imagem publicada); aceitável apenas com o adapter fake.

## 2. Arquivos principais alterados/criados

- Documentos: `docs/22`, `23`, `24`, `25`; `docs/ADR/ADR-005`, `ADR-006`, `ADR-007`; `docs/INDEX.md` e `README.md` (estado atualizado). Documentos 00–21 e ADR-001–004 **não foram alterados** (importados como baseline no commit `aad8812`).
- Contratos: `packages/contracts/src/cecyber_contracts/{manifest,validation,profiles,digest,__main__}.py`, `packages/contracts/schemas/appseclab.v1alpha1.schema.json`.
- Backend: `apps/backend/app/{config,main,deps}.py`, `catalog/`, `sessions/`, `runtime/`, `jobs/`, `workers/`, `audit/`, `identity/`, `shared/`, `db/`; `apps/backend/migrations/versions/0001_engine_core.py`.
- Testes: `packages/contracts/tests/test_manifest.py`, `apps/backend/tests/*`.
- Operação local: `scripts/dev-db.sh`, `scripts/test.sh`, `scripts/demo-slice.sh`, `infrastructure/local/docker-compose.yml`, `.github/workflows/ci.yml`.

## 3. Testes executados e resultados

Ambiente: contêiner Linux de desenvolvimento, PostgreSQL 16 local descartável (`scripts/dev-db.sh`), Python 3.13.18 e 3.12.3.

| Comando | Resultado |
|---|---|
| `uv run ruff check .` / `ruff format --check .` | Sem problemas |
| `uv run mypy packages/contracts/src apps/backend/app` (strict) | `Success: no issues found in 40 source files` |
| `scripts/test.sh` (Python 3.13) | **173 passed** |
| `uv run --python 3.12 pytest` | **173 passed** |
| `uv run alembic upgrade head` → `downgrade base` → `upgrade head` | OK |
| `scripts/demo-slice.sh` (uvicorn + worker reais) | Registro 201; criação 202; replay com a mesma chave retorna a mesma sessão; READY; outro aluno recebe 404; DELETE 202 → TERMINATED; logs JSON com `correlation_id` |

Distribuição: 39 contrato de manifesto; 78 máquina de estados (todas as combinações estado×evento); 9 config/logs; 6 contrato do RuntimePort; 11 integração de catálogo; 30 integração de sessões.

Cenários cobertos (rastreio): ENG-01 (20 requisições concorrentes com mesma chave → 1 sessão e 1 job; 10 chaves distintas → 1 sessão e 9 × `409`), ENG-02 (worker morto: lease recapturado sem provisionamento duplicado), ENG-03/SEC-01 **somente na API REST**, ENG-06 (expiração → limpeza), ENG-07 (nova versão não altera sessão), ENG-08 (suíte de contrato, apenas com o fake), falhas transitórias/permanentes, timeout de readiness, encerramento antes/durante o provisionamento, órfãos e job de término esgotado.

**Não executados:** testes contra adapter real; SEC-02–14; carga; E2E com navegador; ENG-04/05 (reconexão de workspace, reset).

## 4. Decisões tomadas nesta sessão (todas reversíveis e registradas)

1. Documentos importados sem alteração da cópia local, pois o repositório GitHub estava vazio.
2. ADR-005 (modelo acadêmico), ADR-006 (contrato v1alpha1) e ADR-007 (fila em PostgreSQL) **aprovados pelo PO** em 2026-11-11; 006 e 007 implementados, 005 previsto em IMP-401.
3. Premissas não bloqueantes: TTL conta a partir da solicitação e limita a vida total da sessão; `VALIDATING` não é persistido; sessão ativa duplicada → `409 SESSION_ALREADY_ACTIVE`; não-donos recebem `404`; registro de release publica diretamente (sem draft) e é restrito a admin; operações síncronas (SQLAlchemy sync + threadpool do FastAPI) em vez da assinatura `async` ilustrativa de `08 §7`.
4. Autenticação por cabeçalho apenas em `APP_ENV=local|test`; `AUTH_MODE=oidc` e qualquer adapter que não seja `fake` fazem a aplicação recusar o início (fail closed).

## 5. Pendências

- `outbox_events` e dispatcher de eventos de domínio (ADR-007).
- Ajuste editorial sugerido em `12_DATA_MODEL.md` (G-02/G-10) após decisão do ADR-005.

## 6. Bloqueadores

| Bloqueador | Bloqueia | Responsável |
|---|---|---|
| OPEN-01 IdP OIDC | IMP-202 | PO / Arquitetura |
| Inventário on-prem e acesso à infraestrutura | IMP-I01–I03, adapter real, todo código não confiável | PO / Operação |
| ADR-001/002/003 sem PoC | F3, F4 | Plataforma / Segurança |
| OPEN-04 (nota, tentativas, dicas) | F4 (validação e progresso) | PO / Acadêmico |

## 7. Próxima tarefa recomendada

1. **IMP-201** — OpenAPI 3.1 com teste de drift (não depende de decisões).
2. **IMP-203/204/205** — RBAC completo, turmas/atribuições e quotas, com testes negativos.
3. Em paralelo, iniciar **IMP-I01** (inventário on-prem) com o responsável de infraestrutura.
