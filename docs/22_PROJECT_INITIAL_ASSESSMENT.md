# 22. Diagnóstico Inicial do Projeto

| Campo | Valor |
|---|---|
| Produto | CECyber AppSec Labs |
| Versão | 0.1.0 |
| Estado | Diagnóstico técnico para revisão do Product Owner |
| Data | 2026-11-11 |
| Base analisada | Pacote documental v0.3 (30 arquivos Markdown) |
| Autor | Sessão de desenvolvimento assistido por IA (Claude Code) |

> Este documento **não aprova** nenhuma decisão. Ele consolida o que existe, aponta lacunas e contradições e propõe resoluções. Onde uma resolução é proposta, ela está marcada como **Proposta** e só vale após aceite (ADR ou registro em `20_RISKS_AND_DECISIONS.md`).

## 1. Inventário dos arquivos analisados

**Observação de origem:** o repositório GitHub `fbo-sp/appsec-lab` estava vazio (sem commits). Os documentos foram lidos da cópia local `D:\CECyber\Projetos\GitHub\cecyber-appsec-labs` e importados **sem alteração** no primeiro commit da branch de trabalho, para garantir rastreabilidade.

| Arquivo | Tamanho aprox. | Maturidade | Observação |
|---|---|---|---|
| `README.md` | 2,4 KB | Orientativo | Declara estado "planejamento v0.3", sem código |
| `AGENTS.md` | 2,9 KB | Orientativo, útil | Regras de atuação para agentes; fonte principal de conduta |
| `CLAUDE.md` | 0,8 KB | Orientativo | Remete a `AGENTS.md` |
| `docs/INDEX.md` | 2,4 KB | Orientativo | Nenhuma especificação formalmente aprovada |
| `docs/00_PRODUCT_VISION.md` | 12,5 KB | **Detalhado** | Visão, escopo, metas (hipóteses), riscos |
| `docs/01_PROJECT_CHARTER.md` | 1,8 KB | **Esqueleto** | Todas as seções "A desenvolver" |
| `docs/02_PRD.md` | 28 KB | **Detalhado** | FR-001–054, NFR-001–015, BR-001–012, E2E-01–10, OPEN-01–10 |
| `docs/03_FUNCTIONAL_REQUIREMENTS.md` | 2,1 KB | **Esqueleto** | Remete ao PRD + LEX |
| `docs/04_NON_FUNCTIONAL_REQUIREMENTS.md` | 1,9 KB | **Esqueleto** | Remete ao PRD |
| `docs/05_USER_JOURNEYS.md` | 1,9 KB | **Esqueleto** | — |
| `docs/06_SYSTEM_ARCHITECTURE.md` | 7,7 KB | Proposta técnica | C4 L1/L2, módulos, ports, fluxos |
| `docs/07_THREAT_MODEL.md` | 8,6 KB | Proposta técnica | STRIDE TM-01–14, SEC-01–14 |
| `docs/08_LAB_ENGINE_SPEC.md` | 7,6 KB | Proposta implementável | Estados, idempotência, `RuntimePort`, ENG-01–08 |
| `docs/09_PROVISIONING_SPEC.md` | 6,6 KB | Proposta, bloqueada por PoC | Política de workload, gateway, PRV-01–06 |
| `docs/10_VALIDATION_ENGINE_SPEC.md` | 8,5 KB | Proposta técnica | Pipeline, suite, estados de run, VAL-01–08 |
| `docs/11_LAB_MANIFEST_SPEC.md` | 6,6 KB | Proposta detalhada | Manifesto `AppSecLab v1alpha1`, regras de consistência |
| `docs/12_DATA_MODEL.md` | 5,3 KB | Proposta lógica | Tabelas, invariantes, índices |
| `docs/13_API_SPEC.md` | 5,1 KB | Contrato preliminar | Endpoints v0.3, erros, eventos; OpenAPI pendente |
| `docs/14_MVP_SCOPE.md` | 3,9 KB | Proposta de baseline | P0, gates G1–G6 |
| `docs/15_PRODUCT_BACKLOG.md` | 5,1 KB | Sementes | US-001–039, sem estimativa nem aceite detalhado |
| `docs/16_TEST_STRATEGY.md` | 2,1 KB | **Esqueleto** | — |
| `docs/17_MVP_LAB_CATALOG.md` | 2,6 KB | **Esqueleto** + padrão editorial | Conteúdo dos labs ainda não especificado |
| `docs/18_RELEASE_PLAN.md` | 1,9 KB | **Esqueleto** | — |
| `docs/19_OPERATIONS_RUNBOOK.md` | 2,0 KB | **Esqueleto** | — |
| `docs/20_RISKS_AND_DECISIONS.md` | 1,8 KB | **Esqueleto** | Registro de decisões vazio |
| `docs/21_LEARNING_EXPERIENCE_SPEC.md` | 5,9 KB | Requisitos priorizados | LEX-001–006 |
| `docs/ADR/ADR-001-runtime.md` | 1,0 KB | Proposto, pendente | Sem PoC |
| `docs/ADR/ADR-002-isolation.md` | 1,0 KB | Proposto, pendente | Sem PoC |
| `docs/ADR/ADR-003-validation.md` | 1,0 KB | Proposto, pendente | Sem PoC |
| `docs/ADR/ADR-004-on-premises-hosting.md` | 2,8 KB | **Decisão de produto registrada** | Topologia pendente |

Não existia código-fonte, migração, esquema JSON, OpenAPI, pipeline de CI ou infraestrutura como código.

## 2. Resumo da visão do produto

Plataforma própria de laboratórios práticos de AppSec, acessados pelo navegador, em que o aluno **explora e corrige** uma vulnerabilidade por laboratório, num ambiente isolado e efêmero, com editor, terminal, aplicação em execução, etapas guiadas, dicas progressivas e **validação automática por etapa** executada por serviço confiável. O diferencial técnico é um **motor genérico** dirigido por manifestos declarativos e versionados, sem lógica específica de exercício no núcleo. O progresso acadêmico é independente do runtime efêmero. Hospedagem inicial **on-premises** (ADR-004). Integração Moodle/LTI 1.3 é pós-MVP.

## 3. Escopo consolidado do MVP

| Área | Conteúdo P0 | Fonte |
|---|---|---|
| Identidade | OIDC, RBAC (aluno/instrutor/admin), ownership e escopo de turma | FR-001–004 |
| Catálogo | Labs versionados, manifesto validado, release imutável, pipeline de publicação | FR-010–013, `11` |
| Sessões | Criação idempotente, estados formais, reconexão, reset, TTL, encerramento, quotas | FR-020–027, `08` |
| Provisionamento | Sandbox por sessão via adapter, egress deny, limites, reconciliação | `09`, ADR-001/002/004 |
| Workspace | Editor, terminal, preview via gateway autenticado, build/run por comandos aprovados | FR-030–034, LEX-004 |
| Validação | Snapshot, runner protegido, critérios comportamentais, pontuação, feedback, por etapa | FR-040–047, `10`, LEX-005 |
| Pedagogia | Storytelling, 1 CWE principal, etapas, dicas graduais, desbloqueio no backend, variantes no modelo | LEX-001–006 |
| Gestão | Visão de instrutor, CSV, visão operacional, observabilidade, auditoria | FR-050–053 |
| Conteúdo | LAB-001 SQLi (CWE-89), LAB-002 IDOR (CWE-639), LAB-003 JWT (CWE-347), LAB-004 CmdInj (CWE-78, condicionado) | `14` |
| Fora (P1/P2) | LTI 1.3, API de resultados (P1), segunda variante publicada (P1), IA, marketplace, multi-tenant | `14 §4` |

## 4. Estado de maturidade da documentação

| Nível | Documentos | Implicação |
|---|---|---|
| Suficiente para iniciar implementação controlada | 08, 11, 12, 13 (partes), 21 | Permitem implementar contratos, estados e persistência com fake adapter |
| Suficiente como diretriz, não como especificação | 00, 02, 06, 07, 09, 10, 14 | Precisam de ADRs/PoCs para fechar runtime, gateway, runner |
| Esqueletos sem conteúdo | 01, 03, 04, 05, 16, 17, 18, 19, 20 | Não bloqueiam a primeira fatia; bloqueiam piloto e conteúdo dos labs |
| Decisões | Apenas ADR-004 (hospedagem) e o nome do produto estão decididos | Todas as demais alternativas técnicas são **propostas** |

Avaliação geral: **boa profundidade em princípios, segurança e contratos conceituais; baixa profundidade em conteúdo pedagógico concreto, operação, testes e decisões formais.**

## 5. Requisitos já suficientemente definidos para implementação

1. **Máquina de estados da sessão** (FR-021, `08 §3`) — com os ajustes da seção 6 (G-03).
2. **Criação idempotente de sessão** (FR-022, `08 §4`): mesma chave + mesmo corpo = mesma resposta; corpo divergente = `409`.
3. **Contrato de manifesto** `AppSecLab v1alpha1` (`11 §2–3`), incluindo Lab/Variant/Step/Hint e regras de consistência 1–10.
4. **Imutabilidade de release** (FR-012, BR-002): sessão fixa release e variante no início.
5. **Port de runtime** com adapter fake e real satisfazendo o mesmo contrato (`08 §7`, NFR-015, ENG-08).
6. **Separação acadêmico × runtime** (BR-005, `12 §3`): notas e progresso não dependem do runtime.
7. **Erros consistentes** (`13 §5`) e envelope `{"error":{code,message,requestId,details}}`.
8. **Eventos e auditoria** (`08 §8`, `13 §6`): nomes de eventos, `correlation_id`, outbox transacional.
9. **Fail closed** (BR-010) para avaliação e limpeza.
10. **Desbloqueio transacional de etapa** (`12 §3`, LEX-005) — conceito claro; contrato do runner pendente.

## 6. Lacunas e inconsistências encontradas

| ID | Tipo | Descrição | Documentos | Resolução proposta | Impacto |
|---|---|---|---|---|---|
| G-01 | Terminologia | A entidade versionada chama-se `LaboratoryVersion` (PRD, 08), `LabRelease` (11, 12) e "Laboratory Version" (solicitação do PO). | 02, 08, 11, 12 | Tratar como **sinônimos**: nome canônico no código `LabRelease`, exposto na API como `version`. Registrar no glossário. | Baixo |
| G-02 | Terminologia/modelo | "Attempt" significa *submissão para avaliação* no PRD/10/12 (`StepAttempt`), mas o PO definiu **Laboratory Attempt = tentativa de resolução** do laboratório. Além disso `step_progress` está vinculado à **sessão**, contrariando "progresso acadêmico ≠ runtime" e `persistProgressAcrossReset`. | 02, 10, 12, 21, solicitação do PO | **Proposta (ADR-005):** `LabAttempt` = jornada do aluno numa release+variante (dona do `step_progress`, sobrevive a sessões); `LabSession` = runtime efêmero vinculado a um `LabAttempt`; `StepSubmission` = submissão (ex-`StepAttempt`); `ValidationRun` e `ValidationResult`. | **Alto** (modelo de dados acadêmico). Não bloqueia a 1ª fatia, bloqueia EP-VAL. |
| G-03 | Máquina de estados | O diagrama de `08 §3` omite transições que o texto exige: `REQUESTED→FAILED` (job inválido/quota), `REQUESTED/PROVISIONING→TERMINATING` (cancelamento: "qualquer estado não terminal"), `PROVISIONING→EXPIRED`, `VALIDATING→COMPLETED/TERMINATING`. Também não define `FAILED→TERMINATED` quando nada foi provisionado. | 08 | Adotar a tabela (mais completa) como fonte, explicitar todas as transições em código e teste (implementado na 1ª fatia). `VALIDATING` não é persistido como estado de sessão (conforme esclarecimento de `08 §3`). | Médio |
| G-04 | Estados de avaliação | Três vocabulários: `PENDING/PREPARING/RUNNING/SUCCEEDED/FAILED_TESTS/TIMED_OUT/INFRA_ERROR/CANCELLED` (10), `QUEUED/PASSED` (13), `QUEUED/RUNNING/PASSED/FAILED/ERROR` (21). | 10, 13, 21 | Estado **interno** do run = vocabulário de `10`; **projeção pública** = `QUEUED/RUNNING/PASSED/FAILED/ERROR` com mapeamento documentado (`SUCCEEDED`+aprovado→`PASSED`; `SUCCEEDED`/`FAILED_TESTS` reprovado→`FAILED`; `TIMED_OUT`/`INFRA_ERROR`→`ERROR`). | Médio |
| G-05 | API | Rotas do PRD (`/laboratories`, `POST /sessions/{id}/terminate`, `/attempts`) divergem de `13` (`/labs`, `DELETE /sessions/{id}`, `/steps/{stepId}/evaluations`, `/evaluations/{id}`). | 02 §10, 13 | `13` é mais recente (v0.3) e o PRD declara suas rotas como "preliminares": adotar `13`. | Baixo |
| G-06 | Port de runtime | Assinaturas divergentes: `provision(session_id, lab_version, policy)` + `status` (06); `provision(session_id, manifest_digest, policy)` + `inspect` + `reset` (08); `list_owned` (09). | 06, 08, 09 | Consolidar: `provision(ProvisionRequest)`, `inspect(ref)`, `reset(ref, revision)`, `terminate(ref)`, `list_owned()`; request carrega `session_id`, `image_digest`, `runtime_profile`, `resources`, `network`, `expires_at` (contrato de `09 §2`). Implementado na 1ª fatia. | Médio |
| G-07 | Pontuação | Dois modelos: suite com critérios e pesos somando 100 + `minScore` (10 §5) e etapas com `points` + `policy.finalPassingScore` (11). Não há regra de composição. | 10, 11 | **Proposta:** nota do lab = soma de `points` das etapas (soma deve ser 100); critérios da suite determinam aprovação **da etapa**; `finalPassingScore` aplica-se ao lab. Decisão do PO/Acadêmico (OPEN-04). | Médio, bloqueia EP-VAL |
| G-08 | Manifesto | `metadata.status: draft` dentro do manifesto conflita com imutabilidade: estado de publicação é da plataforma, não do artefato. | 11 | Estado de publicação (`draft/published/retired`) é atributo da `LabRelease` no banco; campo no manifesto é **rejeitado** no v1alpha1 implementado (registrado em ADR-006). | Baixo |
| G-09 | Manifesto | Exemplo de LAB-001 em `11` tem 3 etapas; `21 §5` propõe 4 (com "Refletir"/quiz). Tipo de validador para quiz/assertiva não está especificado. | 11, 21 | Permitir `validatorRef` de tipo `knowledge-check` no registro de validadores; definir no EP-VAL. Gate G4 exige ≥3 etapas. | Baixo |
| G-10 | Dados | `lab_sessions` não possui `idempotency_key`; não há tabelas de outbox, jobs de provisionamento, quotas ou grants. `users.role` é único, mas o PRD prevê `RoleAssignment`. `lab_assignments` só por turma, PRD prevê usuário **ou** turma. | 02 §11, 12 | Adicionar `idempotency_key` + `request_fingerprint` em sessões, tabela `outbox_events`/`provisioning_jobs` (implementado), `role_assignments` e atribuição individual opcional (EP-IAM). | Médio |
| G-11 | Mensageria | `06` propõe Redis como fila, mas nenhum ADR existe; o PO pediu "conforme decisão arquitetural". | 06 | **Proposta (ADR-007):** no MVP usar **PostgreSQL** (outbox + fila com `FOR UPDATE SKIP LOCKED` e leases) e adiar Redis até haver necessidade medida. Evita dependência operacional on-prem extra. | Médio, não bloqueante |
| G-12 | Política de sessão | "No máximo uma sessão executável por aluno e lab" (08 §2) interage com a chave de idempotência: chave diferente para o mesmo lab deve retornar a sessão ativa ou `409`? | 08 | Retornar `409 SESSION_ALREADY_ACTIVE` com o `sessionId` existente em `details` (implementado). | Baixo |
| G-13 | Status dos documentos | O PRD intitula a seção 15 de "Complemento **aprovado**", mas `INDEX.md` declara que nada foi aprovado; a Visão está em "0.1.0" mas trata de v0.3. PRD possui duas seções "15". | 00, 02, INDEX | Considerar que LEX-001–006 são **requisitos priorizados pelo PO**, não especificação aprovada. Ajuste editorial sugerido, não realizado. | Baixo |
| G-14 | Backlog | Numeração de épicos fora de ordem (EP13 antes de EP12); histórias sem Given/When/Then, estimativa ou dono; US-010 (reconciliar) referencia FR-026 em vez de FR-025. | 15 | Refinado em `24_IMPLEMENTATION_BACKLOG.md`. | Baixo |
| G-15 | Autenticação | Provedor OIDC indefinido (OPEN-01) e modelo de sessão do portal (cookie vs. bearer) indefinido, o que afeta CSRF e WebSocket. | 02, 13 | Interface de autenticação plugável; **modo de desenvolvimento explícito** apenas com `APP_ENV=local`/`test` (implementado). Decisão de IdP necessária antes de EP-IAM. | **Alto**, não bloqueia a 1ª fatia |
| G-16 | Conteúdo | `17_MVP_LAB_CATALOG.md` vazio: não há narrativa, etapas, dicas, critérios nem aplicação de nenhum dos quatro labs. | 17 | Especificar por lab antes de EP-CONTENT, uma história por lab. | Alto para G4 |
| G-17 | Testes e operação | `16`, `18`, `19`, `20` vazios; não há metas de cleanup (NFR-007 "a definir"), retenção (BR-011) ou SLA. | 16–20 | `23` define estratégia mínima; decisões de SLA/retentiva ficam como pendências. | Médio |
| G-18 | Gateway | Contrato de gateway/WebSocket (tickets, audiência, revogação, origem segregada) só existe em princípio. | 06, 09, 13 | Especificar no EP-GW após PoC; não bloqueia a 1ª fatia. | Alto para workspace |
| G-19 | Variantes e TTL | TTL está em `variants[].session.ttlMinutes` (11) e "45 min" em `08 §4`; recursos estão por variante (11), mas perfis em `09 §7` são por lab. | 08, 09, 11 | TTL e recursos são **por variante**, limitados por teto server-side do `runtimeProfile` (implementado: manifesto não pode exceder o perfil). | Baixo |

### Coerência entre contratos de motor, provisionamento e validadores

- **Motor ↔ provisionamento:** coerentes em princípio (idempotência por `session_id`, nomes determinísticos, reconciliação), divergentes em assinatura (G-06). Resolvido na 1ª fatia.
- **Motor ↔ validação:** a avaliação por **etapa** (v0.3) foi adicionada como adendo em `10`, mas o pipeline principal, o contrato de suite e os estados continuam descritos para avaliação **por laboratório**. Falta: contrato do runner (envelope assinado, canal, identidade), contrato de snapshot (o que é capturado, como o digest é calculado), e o vínculo `validatorRef` → registro protegido → `suite_digest`. **Não há profundidade suficiente para implementar o motor de validação** sem ADR-003 e ADR-005.
- **Manifesto ↔ validação:** `validatorRef` é uma string livre; não há formato, nem registro, nem compatibilidade de versão especificada (regra 6 de `11 §3`).

### Especificações sem profundidade suficiente para implementação

1. Runner de validação e snapshot de workspace (ADR-003).
2. Gateway HTTP/WebSocket, tickets e origem segregada.
3. Runtime real e isolamento (ADR-001/002), incluindo `exec-restricted` para LAB-004.
4. Conteúdo dos quatro laboratórios (`17`).
5. Modelo de turmas, atribuições e relatórios (OPEN-06, OPEN-08).
6. Política de dicas/pontuação/tentativas (OPEN-04, `21 §7`).
7. Retenção LGPD (OPEN-05, BR-011).

## 7. Riscos técnicos prioritários

| ID | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| R-01 | Isolamento insuficiente do sandbox on-prem (escape, rede lateral) | Média | Crítico | PoC comparativa ADR-002, SEC-04–07, gate G5; nada vulnerável em rede compartilhada antes disso |
| R-02 | Infraestrutura on-prem indisponível/indefinida (nós, hipervisor, VLAN, registry, DNS, TLS) | Alta | Alto | Inventário (US-038) como primeiro entregável de infraestrutura; desenvolvimento segue com fake adapter |
| R-03 | Validação forjável ou não determinística | Média | Crítico | Runner fora do workspace, snapshot por digest, envelope autenticado, testes VAL-01–08 |
| R-04 | Acoplamento do motor ao catálogo | Média | Alto | Manifesto + teste "lab benigno sem alteração de código" desde a 1ª fatia; teste de variante simulada |
| R-05 | Ambiguidade do modelo acadêmico (G-02, G-07) gerando retrabalho de dados | Alta | Alto | Decidir ADR-005 antes do EP-VAL |
| R-06 | Órfãos de runtime e vazamento de recursos | Média | Alto | Reconciliador, `list_owned`, nomes determinísticos, ENG-02/06 |
| R-07 | LAB-004 inviável com o runtime disponível | Média | Médio | Gate explícito; lab substituto de menor risco pré-identificado |
| R-08 | Gateway/WebSocket com IDOR ou sequestro de sessão | Média | Crítico | Tickets curtos com audiência, verificação de Origin, SEC-01/03/13 |
| R-09 | Capacidade insuficiente para 30 sessões com P95 ≤ 60 s | Média | Médio | Benchmark na PoC, imagens pequenas, pool aquecido opcional |
| R-10 | Escopo excessivo / ausência de equipe e PO formal definidos | Alta | Alto | Fatias verticais pequenas, gates, backlog sequencial |

## 8. Decisões arquiteturais pendentes

| ID | Decisão | Bloqueia | Estado | Recomendação |
|---|---|---|---|---|
| ADR-001 | Orquestrador/runtime (K8s on-prem?) | Adapter real, US-011 | Proposto, sem PoC | Manter port + fake; PoC com K8s on-prem |
| ADR-002 | Tecnologia de isolamento (gVisor/Kata/microVM) | Qualquer código não confiável; LAB-004 | Proposto, sem PoC | PoC gVisor vs. Kata |
| ADR-003 | Runner e verificação protegida | EP-VAL | Proposto, sem PoC | Controller no plano de controle + workload de avaliação isolado |
| ADR-005 (novo) | Modelo acadêmico `LabAttempt`/`StepSubmission` (G-02) | EP-VAL, EP-PROG | **Proposto nesta entrega** | Aprovar |
| ADR-006 (novo) | Contrato de manifesto v1alpha1 implementado + estado fora do manifesto (G-08, G-19) | — | **Proposto, implementado** | Aprovar |
| ADR-007 (novo) | Fila/mensageria em PostgreSQL no MVP (G-11) | — | **Proposto, implementado** | Aprovar |
| OPEN-01 | Provedor OIDC e modelo de sessão do portal | EP-IAM | Pendente | Decidir antes da fase 2 |
| OPEN-03 | TTL, retomada, reset | Políticas finais | Pendente | Valores configuráveis (45 min / 3 resets) até decisão |
| OPEN-04 | Nota, tentativas, dicas | EP-VAL | Pendente | Ver G-07 |
| OPEN-05 | Retenção LGPD | Piloto | Pendente | — |
| OPEN-09 | Internet nos labs | Manifesto final | Pendente | `deny-all` como único perfil aceito no v1alpha1 |

## 9. Recomendações antes da implementação

1. **Aprovar ADR-005, ADR-006 e ADR-007** (propostos nesta entrega) ou indicar ajustes.
2. **Realizar o inventário on-prem** (US-038): servidores, CPU/RAM/disco, hipervisor, VLANs, firewall, DNS, certificados, storage, registry. Sem isso não há PoC de isolamento.
3. **Definir o IdP OIDC** do piloto (OPEN-01) e o modelo de sessão do portal (cookie HttpOnly + CSRF, recomendado; ou bearer).
4. **Nomear responsáveis** de aceite (PO, Segurança, Operação, Acadêmico) — `01_PROJECT_CHARTER.md` está vazio.
5. **Especificar o conteúdo de LAB-001** em `17` como piloto editorial (narrativa, etapas, dicas, critérios) antes de EP-CONTENT.
6. Continuar o desenvolvimento do plano de controle com **fake adapter**, sem executar código vulnerável fora de ambiente isolado validado.

## 10. Dependências e pré-requisitos de infraestrutura

### Desenvolvimento local (disponível hoje)

| Item | Uso | Estado |
|---|---|---|
| Python 3.12+ | Backend, workers, contratos | Necessário |
| PostgreSQL 16 | Persistência e fila | Necessário (local ou Docker Compose) |
| Docker / Compose | Somente componentes confiáveis de desenvolvimento (PostgreSQL) | Opcional |
| Node.js 22 | Frontend (fase futura) | Futuro |

Nenhum laboratório vulnerável deve ser executado em Docker Compose como fronteira de isolamento.

### On-premises (não verificado; nada pode ser presumido)

| Pré-requisito | Necessário para | Estado |
|---|---|---|
| Inventário de hardware e hipervisor | PoC ADR-001/002 | **Desconhecido** |
| Segmentação de rede (zona administrativa × zona sandbox), firewall, egress deny | NFR-002, ADR-004 | **Desconhecido** |
| Cluster Kubernetes (ou alternativa) com RuntimeClass endurecida | Adapter real | **Não existe** |
| Registry OCI privado com digest/scan/assinatura | FR-013, NFR-012 | **Não existe** |
| DNS interno e certificados TLS (incl. subdomínios segregados para preview) | Gateway | **Não existe** |
| Storage para snapshots/evidências e backup testado | Validação, NFR-008 | **Não existe** |
| PostgreSQL gerenciado internamente com backup/restore | Plano de controle | **Não existe** |
| Stack de observabilidade (coletor OpenTelemetry, métricas, logs) | FR-053, NFR-013 | **Não existe** |
| IdP OIDC | FR-001 | **Não definido** |
