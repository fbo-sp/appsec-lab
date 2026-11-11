# 13. Contratos de API REST e Eventos

| Campo | Valor |
|---|---|
| Produto | CECyber AppSec Labs |
| Versão | 0.3.0 |
| Estado | Contrato preliminar, base para especificação OpenAPI 3.1 |
| Prefixo | `/api/v1` |

## 1. Princípios

Autenticação OIDC; autorização sempre no servidor por escopo/ownership/turma. JSON UTF-8 e timestamps ISO 8601 UTC. `X-Request-Id` para correlação. Operações mutáveis críticas aceitam `Idempotency-Key`. Listagens paginadas com cursor e limites configuráveis. `POST` de sessão/avaliação responde `202 Accepted` quando assíncrono.

## 2. Endpoints principais

| Método | Rota | Papel | Resultado |
|---|---|---|---|
| GET | `/me` | autenticado | perfil e escopos |
| GET | `/labs` | aluno/instrutor | releases publicadas e autorizadas |
| GET | `/labs/{labId}/releases/{version}` | autorizado | narrativa, CWE, objetivos e variantes; sem testes privados |
| GET | `/labs/{labId}/releases/{version}/steps` | autorizado | metas e estado LOCKED/AVAILABLE/PASSED; dicas somente quando desbloqueadas |
| POST | `/sessions` | aluno | inicia sessão para `labId`,`version`,`variantId` |
| GET | `/sessions/{sessionId}` | owner/instrutor autorizado conforme escopo | estado e etapa atual |
| POST | `/sessions/{sessionId}/reset` | owner | reset idempotente |
| DELETE | `/sessions/{sessionId}` | owner/admin | encerramento |
| POST | `/sessions/{sessionId}/steps/{stepId}/evaluations` | owner | cria tentativa e avaliação |
| GET | `/evaluations/{evaluationId}` | owner | status, feedback público e score |
| POST | `/sessions/{sessionId}/steps/{stepId}/hints/{level}/reveal` | owner | dica liberada e uso registrado |
| POST | `/sessions/{sessionId}/workspace/build` | owner | executa build/precompile/run em perfil autorizado |
| GET | `/sessions/{sessionId}/gateway-ticket` | owner | ticket de conexão efêmero e escopado |
| GET | `/reports/completions` | instrutor/admin | resultados filtrados |
| GET | `/reports/completions.csv` | instrutor/admin | exportação segura |
| POST | `/admin/lab-releases` | administrador/pipeline | registra release validada |

## 3. Exemplos JSON

### POST /sessions

```json
{"labId":"LAB-001","version":"1.0.0","variantId":"python-flask"}
```

`202`:

```json
{"sessionId":"018f1a27-1111-7000-a111-111111111111","status":"REQUESTED","statusUrl":"/api/v1/sessions/018f1a27-1111-7000-a111-111111111111"}
```

### GET /sessions/{id}

```json
{"sessionId":"018f1a27-1111-7000-a111-111111111111","status":"ACTIVE","labId":"LAB-001","variantId":"python-flask","currentStepId":"inspect","expiresAt":"2026-11-11T23:00:00Z","steps":[{"id":"inspect","status":"AVAILABLE"},{"id":"exploit","status":"LOCKED"}]}
```

### POST /sessions/{id}/steps/{stepId}/evaluations

```json
{"expectedRevision":"sha256:workspace-snapshot-digest"}
```

`202`: `{"evaluationId":"018f1a27-2222-7000-a222-222222222222","status":"QUEUED"}`

### GET /evaluations/{id}

```json
{"status":"PASSED","stepId":"inspect","score":20,"maxScore":20,"feedback":[{"code":"QUERY_LOCATED","message":"Você identificou o ponto de risco."}],"nextStepId":"exploit"}
```

## 4. Segurança e integridade das etapas

O servidor recusa qualquer operação de avaliação, dica ou acesso especial para etapa `LOCKED`; o frontend não controla o desbloqueio. `GET /steps` devolve metadados de etapas bloqueadas, mas não instruções completas, testes, soluções ou dicas futuras. Tokens de gateway devem expirar rapidamente, ter audiência/escopo de sessão e não ser logados; URLs internas de serviços de laboratório jamais são entregues diretamente sem gateway. `build` aceita apenas `profile/action` permitidos, e nunca execução no backend administrativo.

## 5. Erros consistentes

```json
{"error":{"code":"STEP_LOCKED","message":"Conclua a etapa anterior.","requestId":"req_123","details":{}}}
```

- `400 VALIDATION_ERROR`: payload ou manifesto inválido.
- `401 UNAUTHENTICATED`: sessão de login ausente ou inválida.
- `403 FORBIDDEN`: usuário sem acesso ao recurso.
- `404 NOT_FOUND`: recurso inexistente **ou não visível** ao solicitante.
- `409 CONFLICT`: versão/estado não permite a operação; `STEP_LOCKED`, `SESSION_NOT_READY`, `EVALUATION_IN_PROGRESS`.
- `422 POLICY_VIOLATION`: ação não permitida no perfil/runtime.
- `429 RATE_LIMITED`: excesso de solicitações.
- `503 RUNTIME_UNAVAILABLE`: falha transitória do provisionamento.

## 6. Eventos internos confiáveis

`session.requested`, `session.ready`, `session.failed`, `session.expired`, `evaluation.started`, `evaluation.completed`, `step.unlocked`, `hint.revealed`. Cada evento inclui `event_id`, `schema_version`, `trace_id`, `aggregate_id` e timestamp. Usar outbox transacional para não perder eventos críticos. Eventos são internos e não podem ser emitidos diretamente por sandboxes.

## 7. Contratos ainda pendentes

Produzir arquivo `openapi.yaml`, esquema de WebSocket/gateway, schemas JSON, contrato de runner e testes de contrato. CORS e CSRF conforme modelo de sessão do portal. Taxas de limite e TTL de tickets dependem de ADRs.
