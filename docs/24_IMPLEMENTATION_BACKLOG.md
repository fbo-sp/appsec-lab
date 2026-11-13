# 24. Backlog Executável de Implementação

| Campo | Valor |
|---|---|
| Produto | CECyber AppSec Labs |
| Versão | 0.1.0 |
| Estado | Proposta de refinamento de `15_PRODUCT_BACKLOG.md` |
| Data | 2026-11-11 |

## Convenções

- **ID:** `IMP-<fase><seq>`; cada item referencia a história de origem (`US-xxx`) em `15`.
- **Prioridade:** P0/P1/P2 conforme `15`.
- **Estado:** `Done` só com evidência em `25_DEVELOPMENT_STATUS.md`; `Ready` = dependências satisfeitas; `Blocked` = decisão/infra pendente.
- **Definição de pronto (DoD) comum** (aplica-se a todos os itens, além do DoD específico): código tipado; testes automatizados verdes incluindo negativos; logs estruturados com `correlation_id`; erros no envelope de `13 §5`; sem segredos no repositório; documentação e `25` atualizados; sem afrouxar política de segurança para passar teste.
- Itens são dimensionados para **uma sessão de agente (Codex/Claude Code)**; executar na ordem da seção "Sequência".

## Sequência executável

| Ordem | ID | Título | Fase | Estado |
|---|---|---|---|---|
| 1 | IMP-101 | Estrutura do repositório e ferramentas | F1 | Done |
| 2 | IMP-102 | Contrato de manifesto v1alpha1 e JSON Schema | F1 | Done |
| 3 | IMP-103 | Validação semântica do manifesto | F1 | Done |
| 4 | IMP-104 | Esqueleto FastAPI, erros, correlação e logs JSON | F1 | Done |
| 5 | IMP-105 | Persistência: modelos e migração inicial | F1 | Done |
| 6 | IMP-106 | Registro de release de laboratório | F1 | Done |
| 7 | IMP-107 | Máquina de estados da sessão | F1 | Done |
| 8 | IMP-108 | RuntimePort e FakeRuntimeAdapter | F1 | Done |
| 9 | IMP-109 | Criação idempotente de sessão | F1 | Done |
| 10 | IMP-110 | Worker de provisionamento com fila no PostgreSQL | F1 | Done |
| 11 | IMP-111 | Consulta e encerramento de sessão | F1 | Done |
| 12 | IMP-112 | Reconciliador: TTL e órfãos | F1 | Done |
| 13 | IMP-113 | Auditoria append-only | F1 | Done |
| 14 | IMP-114 | Pipeline de CI | F1 | Done |
| 15 | IMP-201 | OpenAPI 3.1 e testes de contrato | F2 | Ready |
| 16 | IMP-202 | Autenticação OIDC | F2 | Blocked (OPEN-01) |
| 17 | IMP-203 | RBAC, role assignments e ownership | F2 | Ready |
| 18 | IMP-204 | Turmas, matrículas e atribuições | F2 | Ready (OPEN-08 parcial) |
| 19 | IMP-205 | Quotas por usuário, turma e globais | F2 | Ready |
| 20 | IMP-206 | Reset de sessão | F2 | Ready |
| 21 | IMP-207 | Métricas e traces OpenTelemetry | F2 | Ready |
| 22 | IMP-208 | Ciclo de vida de release (draft/published/retired) | F2 | Ready |
| 23 | IMP-209 | Variante simulada (teste de contrato LEX-006) | F2 | Ready |
| 24 | IMP-I01 | Inventário de infraestrutura on-prem | F2-infra | Blocked (acesso à infra) |
| 25 | IMP-I02 | PoC de isolamento comparativa | F2-infra | Blocked (IMP-I01) |
| 26 | IMP-I03 | Segmentação de rede e egress deny | F2-infra | Blocked (IMP-I01) |
| 27 | IMP-301 | KubernetesRuntimeAdapter | F3 | Blocked (ADR-001/002) |
| 27a | IMP-301L | DockerRuntimeAdapter **somente local/test** (ADR-008) | F3 | Done (2026-11-12) |
| 28 | IMP-302 | Workspace gateway e tickets | F3 | Done local (ADR-009, 2026-11-12); produção Blocked (IMP-301) |
| 29 | IMP-303 | Frontend: catálogo e introdução do lab | F3 | Done local (2026-11-12; login OIDC pendente IMP-202) |
| 30 | IMP-304 | Frontend: workspace (editor, terminal, preview) | F3 | Done local (2026-11-12; CodeMirror 6 no lugar de Monaco, ADR-009) |
| 31 | IMP-305 | Ação build/run por perfil aprovado | F3 | Blocked (IMP-301) |
| 32 | IMP-401 | Modelo acadêmico LabAttempt/StepProgress | F4 | Done (migração `0003`, 2026-11-12) |
| 33 | IMP-402 | Snapshot de workspace | F4 | Done local (ADR-010); produção Blocked (ADR-003) |
| 34 | IMP-403 | Validation controller e envelope autenticado | F4 | Parcial local: registro protegido + worker (ADR-010); envelope assinado Blocked (ADR-003) |
| 35 | IMP-404 | Avaliação por etapa e desbloqueio transacional | F4 | Done local (2026-11-12) |
| 36 | IMP-405 | Dicas progressivas e HintUsage | F4 | Done (desconto por dicas conforme ADR-013, 2026-11-13) |
| 37 | IMP-501..504 | Conteúdo LAB-001..004 | F5 | IMP-501 Ready só local (F4 local pronto); demais Blocked (`17`) |
| 38 | IMP-601 | Visão de instrutor e CSV | F6 | Blocked (OPEN-06) |
| 39 | IMP-602 | Visão operacional admin | F6 | Ready após F2 |
| 40 | IMP-603 | Carga 30 sessões | F6 | Blocked (F3) |
| 41 | IMP-604 | Bateria adversarial SEC-01–14 | F6 | Blocked (F3/F4) |

---

## Épico EP-FND — Fundação (F1)

### IMP-101 — Estrutura do repositório e ferramentas
- **Descrição:** criar estrutura `apps/`, `packages/`, `laboratories/`, `infrastructure/`, `scripts/`, `tests/`; `pyproject` com ruff, mypy, pytest; `.gitignore`, `.env.example`.
- **Prioridade:** P0 · **Requisitos:** NFR-012 (rastreabilidade), regras de engenharia · **Dependências:** — · **Componentes:** repositório
- **Aceite:** `scripts/test.sh` executa toda a suíte a partir de um clone limpo; nenhum diretório vazio sem README explicando propósito e fase.
- **Testes:** execução de `ruff`, `mypy` e `pytest`.
- **DoD:** comum.

### IMP-102 — Contrato de manifesto v1alpha1 e JSON Schema
- **Descrição:** modelos Pydantic estritos (`extra=forbid`) para `AppSecLab` (metadata, learning/story, variants, steps, hints, policy) em `packages/contracts`; exportar `schemas/appseclab.v1alpha1.schema.json`.
- **Prioridade:** P0 · **Requisitos:** FR-011, LEX-001/002/003/006, `11 §2` · **Dependências:** IMP-101 · **Componentes:** contracts
- **Aceite:** manifesto de exemplo benigno valida; campos desconhecidos rejeitados; `apiVersion`/`kind` fora da allowlist rejeitados; schema exportado idêntico ao gerado (teste de drift).
- **Testes:** unitários positivos/negativos; teste de drift do schema.
- **DoD:** comum + ADR-006 proposto.

### IMP-103 — Validação semântica do manifesto
- **Descrição:** regras de `11 §3`: unicidade de ids/ordens de etapa, ordens contíguas, níveis de dica únicos, CWE no formato `CWE-<n>`, digest `sha256:<64 hex>` real (rejeitar placeholder), soma de pontos = 100, `finalPassingScore` ≤ 100, `validatorRef` com formato válido, comandos como lista (sem shell), recursos ≤ teto do `runtimeProfile`, `egressProfile=deny-all`, TTL dentro do limite.
- **Prioridade:** P0 · **Requisitos:** FR-011/013, BR-009, `11 §3`, `09 §2` · **Dependências:** IMP-102 · **Componentes:** contracts
- **Aceite:** cada regra tem ao menos um teste negativo com mensagem localizada (`loc`).
- **Testes:** unitários parametrizados.
- **DoD:** comum. Regra 6 (existência no registro de validadores) implementada em 2026-11-12 (`UNKNOWN_VALIDATOR`).

### IMP-104 — Esqueleto FastAPI, erros, correlação e logs JSON
- **Descrição:** app factory, settings via ambiente, middleware `X-Request-Id`, formatter JSON, envelope de erro `13 §5`, `GET /healthz`, autenticação de desenvolvimento só em `APP_ENV=local|test`.
- **Prioridade:** P0 · **Requisitos:** FR-053, NFR-013, `13 §1/§5` · **Dependências:** IMP-101 · **Componentes:** backend/shared, identity
- **Aceite:** toda resposta tem `X-Request-Id`; erros com `requestId`; app recusa iniciar com auth de dev fora de local/test.
- **Testes:** integração HTTP; teste de configuração negativa.
- **DoD:** comum.

### IMP-105 — Persistência: modelos e migração inicial
- **Descrição:** SQLAlchemy 2 + Alembic; tabelas `labs`, `lab_releases`, `lab_variants`, `lab_steps`, `step_hints`, `lab_sessions` (com `idempotency_key`, `request_fingerprint`, `version_num`), `runtime_instances`, `jobs`, `audit_events`. (`outbox_events` para eventos de domínio foi adiada, ver ADR-007.)
- **Prioridade:** P0 · **Requisitos:** `12`, ADR-007 · **Dependências:** IMP-101 · **Componentes:** backend/db
- **Aceite:** `alembic upgrade head` e `downgrade base` funcionam em PostgreSQL 16; constraints únicas de `12 §2` presentes; índice parcial garante uma sessão ativa por usuário+release.
- **Testes:** integração de migração; testes de constraint.
- **DoD:** comum.

### IMP-106 — Registro de release de laboratório
- **Descrição:** `POST /api/v1/admin/lab-releases` recebe manifesto (YAML/JSON), valida, calcula `manifest_digest` canônico, persiste release + variantes + etapas + dicas. Mesmo `(lab_id, version)` e mesmo digest = idempotente (`200`); digest diferente = `409 RELEASE_IMMUTABLE`. `GET /api/v1/labs` e `GET /api/v1/labs/{labId}/releases/{version}` (sem `validatorRef`).
- **Prioridade:** P0 · **Requisitos:** FR-010/011/012, BR-002, US-004/005/006 · **Dependências:** IMP-103/105 · **Componentes:** catalog
- **Aceite:** apenas admin registra; release benigna registrada sem mudança de código; resposta pública não expõe `validatorRef`.
- **Testes:** integração positiva, idempotência, imutabilidade, autorização (aluno → `403`).
- **DoD:** comum.

### IMP-107 — Máquina de estados da sessão
- **Descrição:** enum `SessionStatus` e tabela explícita de transições (`08 §3` + G-03); função pura `transition()` que lança `InvalidTransition`.
- **Prioridade:** P0 · **Requisitos:** FR-021, `08 §3` · **Dependências:** IMP-101 · **Componentes:** sessions
- **Aceite:** 100% das combinações estado×evento cobertas por teste; terminais não saem.
- **Testes:** unitários exaustivos.
- **DoD:** comum.

### IMP-108 — RuntimePort e FakeRuntimeAdapter
- **Descrição:** `RuntimePort` consolidado (G-06): `provision`, `inspect`, `reset`, `terminate`, `list_owned`; `ProvisionRequest` conforme `09 §2`; `FakeRuntimeAdapter` determinístico, idempotente, com injeção de falhas; suíte de contrato reutilizável.
- **Prioridade:** P0 · **Requisitos:** NFR-015, ENG-08, `08 §7`, `09 §4` · **Dependências:** IMP-101 · **Componentes:** runtime
- **Aceite:** provisionar 2× o mesmo `session_id` retorna o mesmo ref; terminar 2× é seguro; política divergente para o mesmo `session_id` gera conflito.
- **Testes:** suíte de contrato parametrizada por adapter.
- **DoD:** comum. **Limitação:** fake não prova isolamento.

### IMP-109 — Criação idempotente de sessão
- **Descrição:** `POST /api/v1/sessions` (`labId`, `version`, `variantId`, header `Idempotency-Key` obrigatório); valida release publicada e variante; numa transação cria sessão `REQUESTED`, job de provisionamento e evento outbox. Mesma chave+corpo = mesma resposta; corpo diferente = `409 IDEMPOTENCY_KEY_REUSED`; sessão ativa existente para a mesma release = `409 SESSION_ALREADY_ACTIVE`.
- **Prioridade:** P0 · **Requisitos:** FR-020/022, BR-001/002, ENG-01, E2E-03 · **Dependências:** IMP-105/106/107 · **Componentes:** sessions
- **Aceite:** 20 requisições concorrentes com mesma chave → 1 sessão, 1 job.
- **Testes:** integração + concorrência real com PostgreSQL.
- **DoD:** comum. **Pendente:** verificação de atribuição (IMP-204) e quotas (IMP-205).

### IMP-110 — Worker de provisionamento com fila no PostgreSQL
- **Descrição:** fila em `jobs` com `FOR UPDATE SKIP LOCKED`, lease com expiração, tentativas limitadas com backoff; executa `PROVISION`/`TERMINATE`; transições persistidas com optimistic locking.
- **Prioridade:** P0 · **Requisitos:** FR-020/025/026, ENG-02, PRV-03, ADR-007 · **Dependências:** IMP-108/109 · **Componentes:** workers
- **Aceite:** falha transitória reprocessa; excedendo tentativas → `FAILED` e limpeza; lease expirado é retomado por outro worker sem duplicar runtime.
- **Testes:** integração com falhas injetadas e lease expirado.
- **DoD:** comum.

### IMP-111 — Consulta e encerramento de sessão
- **Descrição:** `GET /api/v1/sessions/{id}` (ownership; `404` para não-donos); `DELETE /api/v1/sessions/{id}` com `Idempotency-Key` → `TERMINATING` + job; worker termina runtime e confirma ausência via `inspect` antes de `TERMINATED`.
- **Prioridade:** P0 · **Requisitos:** FR-023/026, FR-002 (parcial), ENG-03 (API), SEC-01 (API) · **Dependências:** IMP-110 · **Componentes:** sessions, workers
- **Aceite:** B recebe `404` para sessão de A; encerramento repetido retorna `202` sem novo job duplicado; `TERMINATED` só após runtime ausente.
- **Testes:** integração.
- **DoD:** comum.

### IMP-112 — Reconciliador: TTL e órfãos
- **Descrição:** varredura periódica: sessões com `expires_at` vencido → `EXPIRED` → `TERMINATING`; runtimes de `list_owned()` sem sessão viva → `terminate`; jobs com lease vencido → re-enfileirar.
- **Prioridade:** P0 · **Requisitos:** FR-025, NFR-007, ENG-06, TM-14 · **Dependências:** IMP-110 · **Componentes:** workers
- **Aceite:** sessão expirada chega a `TERMINATED` sem runtime; órfão injetado no adapter é removido e auditado.
- **Testes:** integração com relógio controlado.
- **DoD:** comum. **Pendente:** SLA de cleanup (NFR-007).

### IMP-113 — Auditoria append-only
- **Descrição:** `audit_events` gravado na mesma transação das ações (registro de release, criação/encerramento/expiração/falha de sessão, órfão removido); sem segredos/PII além de ids.
- **Prioridade:** P0 · **Requisitos:** NFR-010, BR-008, FR-053 · **Dependências:** IMP-105 · **Componentes:** audit
- **Aceite:** trilha reconstrói o ciclo de vida da sessão; papel de banco da aplicação sem `UPDATE/DELETE` (pendente: papéis de BD em F2).
- **Testes:** integração verifica eventos por fluxo.
- **DoD:** comum.

### IMP-114 — Pipeline de CI
- **Descrição:** workflow GitHub Actions: ruff, mypy, pytest com serviço PostgreSQL 16, verificação de drift do JSON Schema, scan de segredos.
- **Prioridade:** P0 · **Requisitos:** FR-013, NFR-012 · **Dependências:** IMP-101–113 · **Componentes:** CI
- **Aceite:** PR mostra status verde/vermelho; falha de teste bloqueia merge (proteção de branch é configuração do PO).
- **Testes:** execução do workflow.
- **DoD:** comum.

## Épico EP-CTRL — Plano de controle completo (F2)

### IMP-201 — OpenAPI 3.1 e testes de contrato
- **Descrição:** publicar `packages/contracts/openapi.yaml` gerado e revisado; testes que comparam rotas/esquemas implementados ao contrato. **Req.:** `13 §7`, NFR-015 · **Dep.:** IMP-111 · **Comp.:** contracts, backend · **P0**
- **Aceite:** drift entre implementação e contrato falha o CI. **Testes:** contrato. **DoD:** comum.

### IMP-202 — Autenticação OIDC
- **Descrição:** login OIDC (Authorization Code + PKCE), sessão de portal (recomendado: cookie HttpOnly + CSRF), logout, `GET /api/v1/me`, mapeamento `idp_subject → users`. **Req.:** FR-001, TM-01/13 · **Dep.:** OPEN-01 · **Comp.:** identity · **P0**
- **Aceite:** token inválido/expirado → `401`; CSRF ausente em mutação → `403`; e-mail não é chave de autorização. **Testes:** integração com IdP de teste (ex.: Keycloak em container de dev — ADR). **DoD:** comum.

### IMP-203 — RBAC, role assignments e ownership
- **Descrição:** `role_assignments`, dependências FastAPI de autorização por papel + ownership + escopo de turma em todas as rotas. **Req.:** FR-002/003, SEC-01 · **Dep.:** IMP-104 · **Comp.:** identity · **P0**
- **Aceite:** matriz `02 §3` coberta por teste parametrizado; instrutor não acessa terminal de aluno. **Testes:** autorização negativa por rota. **DoD:** comum.

### IMP-204 — Turmas, matrículas e atribuições
- **Descrição:** `cohorts`, `enrollments`, `lab_assignments` (turma e, opcionalmente, usuário — G-10); `POST /sessions` exige atribuição vigente. **Req.:** FR-004, BR-001 · **Dep.:** IMP-203 · **Comp.:** cohorts, catalog · **P0**
- **Aceite:** aluno não atribuído → `403`/`404`; fora da janela `start_at/end_at` → `409`. **Testes:** integração. **DoD:** comum.

### IMP-205 — Quotas
- **Descrição:** reserva atômica de quota (usuário, turma, global, pool) na criação; liberação no término. **Req.:** FR-027, TM-11 · **Dep.:** IMP-109 · **Comp.:** sessions · **P0**
- **Aceite:** concorrência não ultrapassa quota; `429`/`409 QUOTA_EXCEEDED` explicável. **Testes:** concorrência. **DoD:** comum.

### IMP-206 — Reset de sessão
- **Descrição:** `POST /sessions/{id}/reset` idempotente, limite configurável (3), serializado contra avaliação; nova `workspace_revision`; preserva histórico. **Req.:** FR-024, BR-005, ENG-05 · **Dep.:** IMP-111, OPEN-03 (valores) · **Comp.:** sessions, runtime · **P0**
- **Aceite:** 4º reset → `409 RESET_LIMIT`; reset durante avaliação → `409`. **Testes:** integração. **DoD:** comum.

### IMP-207 — OpenTelemetry
- **Descrição:** traces e métricas (`session_provision_duration_seconds`, `active_sandboxes`, `cleanup_age_seconds`, falhas por etapa) via OTLP; labels sem PII. **Req.:** FR-053, NFR-013, `02 §14` · **Dep.:** IMP-110 · **Comp.:** shared, workers · **P0**
- **Aceite:** métricas visíveis num coletor local; nenhum label com e-mail. **Testes:** unitário de instrumentação + verificação manual. **DoD:** comum + ADR para stack de observabilidade on-prem.

### IMP-208 — Ciclo de vida de release
- **Descrição:** `draft → published → retired`; drafts só para homologadores; retirada bloqueia novas sessões, mantém existentes conforme política. **Req.:** FR-012/014, `02 §9` · **Dep.:** IMP-106 · **Comp.:** catalog · **P0/P1**
- **Aceite:** sessão nova em release `retired` → `409`. **Testes:** integração. **DoD:** comum.

### IMP-209 — Variante simulada
- **Descrição:** manifesto de teste com duas variantes (ex.: `python`, `node`) mapeando as mesmas etapas; sessões por variante abrem perfis diferentes. **Req.:** LEX-006, US-037, `11 §6` · **Dep.:** IMP-109 · **Comp.:** contracts, sessions · **P0**
- **Aceite:** passos idênticos para ambas; validação rejeita variantes com perfis não permitidos. **Testes:** contrato. **DoD:** comum.

## Épico EP-INFRA — On-premises (F2-infra)

### IMP-I01 — Inventário de infraestrutura
- **Descrição:** levantar servidores, CPU/RAM/disco, hipervisor, rede (VLAN/firewall), DNS, PKI, storage, backup, equipe de operação; registrar em `docs/26_ONPREM_INVENTORY.md`. **Req.:** ADR-004, US-038 · **Dep.:** acesso/responsável de infra · **Comp.:** infra · **P0**
- **Aceite:** inventário revisado por Operação. **Testes:** n/a (documental). **DoD:** documento aprovado.

### IMP-I02 — PoC de isolamento comparativa
- **Descrição:** K8s descartável on-prem com gVisor e Kata; mesmas suítes SEC-04/05/06/11/14 e métricas de startup. **Req.:** ADR-001/002, `09 §8` · **Dep.:** IMP-I01 · **Comp.:** infra · **P0**
- **Aceite:** ADR-001/002 atualizados com evidência e sign-off de Segurança. **Testes:** SEC-04–06/11/14. **DoD:** ADR aprovado.

### IMP-I03 — Segmentação de rede e egress deny
- **Descrição:** desenho e aplicação de zonas (administrativa, sandbox, borda); NetworkPolicy default-deny + enforcement de firewall. **Req.:** NFR-002, TM-06 · **Dep.:** IMP-I01 · **Comp.:** infra · **P0**
- **Aceite:** SEC-06 (RFC1918, metadata, lateral) bloqueado. **Testes:** SEC-06. **DoD:** evidência registrada.

## Épico EP-WS — Workspace (F3)

### IMP-301L — DockerRuntimeAdapter local (ADR-008)
- **Descrição:** adapter `docker-local` do `RuntimePort` restrito a `APP_ENV=local|test`; rede interna por sessão, não-root, raiz somente leitura, limites, endpoint interno persistido (`0002`) para o gateway. **Aceite:** suíte de contrato + `test_docker_local_isolation.py` com Docker real; `smoke-compose.sh --docker-runtime`. **Não** comprova isolamento para código hostil.

### IMP-301 — KubernetesRuntimeAdapter
- **Descrição:** adapter real satisfazendo a suíte de contrato de IMP-108; Pod/NetworkPolicy/RuntimeClass por sessão, nomes determinísticos, labels de ownership. **Req.:** `09 §3–4`, ENG-08, PRV-01–05 · **Dep.:** ADR-001/002 · **P0**
- **Aceite:** mesma suíte de contrato do fake verde; `list_owned` por label. **Testes:** contrato + SEC-04/05. **DoD:** comum.

### IMP-302 — Workspace gateway e tickets
- **Descrição:** `GET /sessions/{id}/gateway-ticket` (curto, audiência, finalidade); gateway HTTP/WS que resolve `session_id → runtime_ref`; revogação no término/expiração. **Req.:** FR-032/033, NFR-014, TM-03/13 · **Dep.:** IMP-301 · **P0**
- **Aceite:** ticket de A não funciona para B; Origin inválida negada; ticket revogado em ≤ N s. **Testes:** SEC-01/03/13. **DoD:** comum + ADR do gateway.

### IMP-303 — Frontend: catálogo e introdução
- **Descrição:** React+TS: catálogo, página do lab (storytelling, CWE, objetivos, variante). **Req.:** FR-010/030, LEX-001 · **Dep.:** IMP-106, IMP-202 · **P0**
- **Aceite:** sem lógica de desbloqueio no cliente. **Testes:** unitários de componentes + E2E básico. **DoD:** comum.

### IMP-304 — Frontend: workspace
- **Descrição:** Monaco, xterm.js, preview em origem segregada, estados da sessão e timer. **Req.:** FR-030–034, LEX-004, `21 §4` · **Dep.:** IMP-302 · **P0**
- **Aceite:** E2E-01 com lab benigno. **Testes:** Playwright. **DoD:** comum.

### IMP-305 — Build/run por perfil aprovado
- **Descrição:** `POST /sessions/{id}/workspace/build` executa somente comandos do manifesto aprovado dentro do sandbox. **Req.:** LEX-004, US-036, `13 §4` · **Dep.:** IMP-301 · **P0**
- **Aceite:** ação fora do perfil → `422 POLICY_VIOLATION`; nada executa no backend. **Testes:** integração + negativo. **DoD:** comum.

## Épico EP-VAL — Validação e progressão (F4)

### IMP-401 — Modelo acadêmico
- **Descrição:** `lab_attempts`, `step_progress` por attempt, `step_submissions`, `validation_runs`, `criterion_results`, `lab_completions` (ADR-005). **Req.:** BR-005, `12 §3`, LEX-005 · **Dep.:** ADR-005 · **P0**
- **Aceite:** progresso sobrevive a encerramento/reset/expiração da sessão. **Testes:** integração. **DoD:** comum.

### IMP-402 — Snapshot de workspace
- **Descrição:** captura consistente de artefatos selecionados, digest, armazenamento imutável. **Req.:** FR-041, VAL-03 · **Dep.:** ADR-003, IMP-301 · **P0**
- **Aceite:** edição pós-snapshot não altera digest nem resultado. **Testes:** concorrência. **DoD:** comum.

### IMP-403 — Validation controller e envelope autenticado
- **Descrição:** serviço separado (`services/validator`) que carrega suite por digest de registro protegido, executa em workload isolado e devolve envelope assinado; backend valida emissor/vínculo/unicidade. **Req.:** FR-042/043, BR-006, TM-07/08 · **Dep.:** ADR-003 · **P0**
- **Aceite:** VAL-04/05/07. **Testes:** negativos (forja, replay, timeout). **DoD:** comum.

### IMP-404 — Avaliação por etapa e desbloqueio transacional
- **Descrição:** `POST /sessions/{id}/steps/{stepId}/evaluations`; uma avaliação RUNNING por sessão; `PASSED` desbloqueia próxima etapa na mesma transação; `ERROR` não desbloqueia nem penaliza. **Req.:** FR-040/044/047, LEX-005, US-035 · **Dep.:** IMP-401/403 · **P0**
- **Aceite:** etapa `LOCKED` → `409 STEP_LOCKED`; VAL-06. **Testes:** concorrência + negativos. **DoD:** comum.

### IMP-405 — Dicas progressivas
- **Descrição:** `POST .../hints/{level}/reveal` em ordem; `hint_usage` append-only; penalidade só se configurada. **Req.:** FR-035, LEX-005, US-034 · **Dep.:** IMP-401, OPEN-04 · **P0**
- **Aceite:** nível 3 sem nível 2 → `409`; dica de etapa bloqueada → `409`. **Testes:** integração. **DoD:** comum.

## Épico EP-CONTENT — Laboratórios (F5)

### IMP-501..504 — LAB-001 SQLi, LAB-002 IDOR, LAB-003 JWT, LAB-004 Command Injection
- **Descrição:** um item por lab: especificação em `17`, aplicação realista, manifesto, ≥3 etapas, dicas, validadores privados positivos/negativos/regressão. **Req.:** US-022–025, US-031/032, LEX-001–005, `14 §3` · **Dep.:** F4 + especificação aprovada; LAB-004 também G5 de contenção · **P0 (LAB-004 condicionado)**
- **Aceite:** G4; VAL-01/02 por lab; nenhum código de plataforma alterado para incluir o lab. **Testes:** suíte de validadores contra soluções corretas, incorretas e adversariais. **DoD:** comum + revisão pedagógica.

## Épico EP-OPS — Gestão e prontidão (F6)

### IMP-601 — Visão de instrutor e CSV
- **Req.:** FR-050/051, E2E-10 · **Dep.:** IMP-204, OPEN-06 · **Aceite:** só turmas atribuídas; campos aprovados. **Testes:** autorização negativa. **P0**

### IMP-602 — Visão operacional admin
- **Req.:** FR-052 · **Dep.:** F2 · **Aceite:** lista sessões, falhas, órfãos; encerramento administrativo auditado. **Testes:** integração. **P0**

### IMP-603 — Carga 30 sessões
- **Req.:** NFR-003/004/005, E2E-04 · **Dep.:** F3 · **Aceite:** relatório com P95 e taxa de sucesso no ambiente piloto. **Testes:** carga. **P0**

### IMP-604 — Bateria adversarial
- **Req.:** SEC-01–14, G5 · **Dep.:** F3/F4 · **Aceite:** zero críticos abertos; parecer de Segurança. **Testes:** automatizados + red team. **P0**
