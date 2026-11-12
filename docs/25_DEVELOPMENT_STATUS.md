# 25. Status de Desenvolvimento

> **Leia antes de qualquer nova sessão de IA:** este arquivo, `24_IMPLEMENTATION_BACKLOG.md`, `22_PROJECT_INITIAL_ASSESSMENT.md` e `docs/ADR/`. Não declare tarefa concluída sem evidência verificável (comando + resultado).

| Campo | Valor |
|---|---|
| Atualizado em | 2026-11-12 |
| Fase atual | F1 concluída; **F3 local** iniciada rumo ao primeiro laboratório visual (ADR-008) |
| Branch | `claude/project-thread-arhml7` |
| Última entrega concluída | IMP-301L — runtime Docker local: LAB-000 executa como contêiner real e é removido ao encerrar |

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
| Ambiente local Docker | `apps/backend/Dockerfile` (non-root, uid 10001), `infrastructure/local/docker-compose.yml` (PostgreSQL + migrate + API + worker, portas só em 127.0.0.1), `scripts/demo-local.ps1` (Windows), `scripts/smoke-compose.sh` (também no CI) | Execução no Docker Desktop do PO (Windows) |
| IMP-301L Runtime Docker local (ADR-008) | `DockerRuntimeAdapter` restrito a `APP_ENV=local\|test`: rede `internal` por sessão, não-root obrigatório, raiz somente leitura, `cap_drop=ALL`, limites, sem portas no host; endpoint interno persistido (migração `0002`); imagem do LAB-000 em `laboratories/LAB-000-hello-benign/runtime/`; `scripts/lab-local.sh`/`.ps1`; override `docker-compose.docker-runtime.yml` (socket só no worker) | **Não** é isolamento para código hostil; `reset` não suportado; sem gateway ainda (aplicação não acessível pelo navegador) |
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
| `uv run mypy packages/contracts/src apps/backend/app` (strict) | `Success: no issues found in 41 source files` |
| `DOCKER_CONTRACT_TESTS=1 scripts/test.sh` (2026-11-12, Python 3.12, Docker 29 Linux) | **189 passed** (inclui suíte de contrato e controles com Docker real) |
| `uv run alembic upgrade head` → `downgrade base` → `upgrade head` (0001+0002) | OK |
| `scripts/smoke-compose.sh --no-build --docker-runtime` (2026-11-12) | LAB-000 registrado com ID local da imagem; READY; contêiner uid 10001, raiz somente leitura, rede interna, sem portas no host, app responde dentro da sessão; TERMINATED; contêiner, rede e volume removidos |
| `scripts/smoke-compose.sh --no-build` (Docker 29, Linux) | Pilha sobe saudável; registro 201; READY; intruso 404; TERMINATED; API roda como uid 10001 |
| `scripts/demo-slice.sh` (uvicorn + worker reais) | Registro 201; criação 202; replay com a mesma chave retorna a mesma sessão; READY; outro aluno recebe 404; DELETE 202 → TERMINATED; logs JSON com `correlation_id` |

Distribuição: 39 contrato de manifesto; 78 máquina de estados; 12 config/logs; 12 contrato do RuntimePort (6 fake + 6 Docker); 7 controles do adapter Docker (endurecimento, sem egresso, sem alcance entre sessões, workspace gravável/raiz não, imagem root recusada, imagem desconhecida, contêiner alheio intocado); 11 integração de catálogo; 31 integração de sessões. Sem `DOCKER_CONTRACT_TESTS=1` os testes Docker aparecem como *skipped*. O teste de "sem egresso" no contêiner de desenvolvimento tem valor limitado porque esse ambiente já restringe a rede; no CI (runner com Internet) ele é significativo.

Cenários cobertos (rastreio): ENG-01 (20 requisições concorrentes com mesma chave → 1 sessão e 1 job; 10 chaves distintas → 1 sessão e 9 × `409`), ENG-02 (worker morto: lease recapturado sem provisionamento duplicado), ENG-03/SEC-01 **somente na API REST**, ENG-06 (expiração → limpeza), ENG-07 (nova versão não altera sessão), ENG-08 (suíte de contrato, apenas com o fake), falhas transitórias/permanentes, timeout de readiness, encerramento antes/durante o provisionamento, órfãos e job de término esgotado.

**Não executados:** adapter de produção (ADR-001/002); SEC-02–14; carga; E2E com navegador; ENG-04/05 (reconexão de workspace, reset).

## 4. Decisões tomadas nesta sessão (todas reversíveis e registradas)

1. Documentos importados sem alteração da cópia local, pois o repositório GitHub estava vazio.
2. ADR-005 (modelo acadêmico), ADR-006 (contrato v1alpha1) e ADR-007 (fila em PostgreSQL) **aprovados pelo PO** em 2026-11-11; 006 e 007 implementados, 005 previsto em IMP-401.
3. Premissas não bloqueantes: TTL conta a partir da solicitação e limita a vida total da sessão; `VALIDATING` não é persistido; sessão ativa duplicada → `409 SESSION_ALREADY_ACTIVE`; não-donos recebem `404`; registro de release publica diretamente (sem draft) e é restrito a admin; operações síncronas (SQLAlchemy sync + threadpool do FastAPI) em vez da assinatura `async` ilustrativa de `08 §7`.
4. ADR-008 (runtime Docker só local/test) aprovado pelo PO em 2026-11-12.
5. Autenticação por cabeçalho apenas em `APP_ENV=local|test`; `AUTH_MODE=oidc` e qualquer adapter que não seja `fake` fazem a aplicação recusar o início (fail closed).

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

Rumo ao primeiro laboratório visual (preferência do PO: testar manualmente só com interface):
1. **IMP-302 local** — gateway de workspace com tickets (preview HTTP, arquivos, terminal), conectado só às redes das sessões.
2. **IMP-303–305** — interface React: catálogo, introdução, etapas, editor, terminal, preview.
3. **IMP-401–405** — validação, progresso e dicas (depende de OPEN-04: penalidade de dicas e tentativas).
4. **IMP-501** — LAB-001 SQL Injection (somente local).
Em paralelo: IMP-I01 (inventário on-prem).
