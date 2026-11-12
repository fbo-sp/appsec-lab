# ADR-011: Prazo da sessão com renovação e indicadores de provisionamento

- **Status:** Proposto, implementado (2026-11-12), a pedido do PO após testar o LAB-000.
- **Data:** 2026-11-12
- **Relacionados:** ADR-006 (contrato do manifesto), ADR-008 (runtime local), FR-025/NFR-007 (expiração e limpeza), IMP-207 (observabilidade)

## Contexto

O PO pediu duas coisas:
- um tempo máximo para cada ambiente, configurável por laboratório, com aviso ao aluno antes do fim e opção de renovar;
- o registro do tempo de subida de cada ambiente, para gerar indicadores ao administrador.

A expiração por `ttlMinutes` e o reconciliador já existiam. A suspeita de um ambiente ativo por 7 horas foi investigada no computador do PO em 2026-11-12. Nenhuma sessão passou do prazo: a sessão expirou por TTL e foi removida, e o computador ficou suspenso por cerca de 6h45. O que ficou na tela foi uma aba desatualizada.

## Decisão

1. **Prazo por laboratório.**
   - `variants[].session.ttlMinutes` continua sendo o prazo da sessão.
   - Novo campo opcional `session.maxRenewals` (0–10, padrão 2). É uma adição compatível ao `v1alpha1`, e o JSON Schema foi regenerado.
2. **Renovação** (`POST /api/v1/sessions/{id}/renewals`):
   - só o dono renova;
   - só em `READY`/`ACTIVE` e antes de expirar;
   - só na janela final, que é `min(5, max(1, ttl/3))` minutos;
   - até `maxRenewals` vezes.
   - Cada renovação define `expires_at = agora + ttlMinutes` e é auditada (`session.renewed`).
   - Erros: `RENEWAL_TOO_EARLY`, `RENEWAL_LIMIT_REACHED` e `SESSION_NOT_READY`.
   - A visão da sessão expõe `ttlMinutes`, `renewals`, `maxRenewals` e `renewableAt`.
   - Sem renovação, o reconciliador expira a sessão e remove o ambiente como antes. O progresso fica na tentativa (ADR-005).
3. **Inatividade** é tratada pelo próprio prazo: quem não está usando não renova, e o ambiente é removido no fim do prazo. Não há heartbeat do navegador. Essa escolha evita que uma aba esquecida mantenha o ambiente vivo.
4. **Interface.**
   - Nos últimos 5 minutos o timer fica em destaque.
   - Na janela de renovação abre um aviso com "Renovar por N min" e "Agora não".
   - Sem renovações restantes, aparece um aviso fixo de que o progresso fica salvo.
   - O portal revalida a sessão ao voltar para a aba ou ao ganhar foco, por exemplo depois de o computador acordar.
5. **Indicadores.**
   - A migração `0004` adiciona `lab_sessions.ready_at`, `provision_ms` e `renewals`, além de `lab_variants.max_renewals`.
   - O worker grava o tempo da solicitação até `READY` e registra o log `session.ready` com `provision_ms`.
   - `GET /api/v1/admin/metrics/provisioning?days=30` (só admin) devolve, por laboratório, versão e variante:
     - total de sessões, prontas e falhas;
     - média, p50, p95 e máximo do tempo de subida;
     - total de renovações.

## Consequências

- Um teto global de renovações ou de duração por organização fica para IMP-205 (quotas).
- Um painel visual para o administrador ainda não existe; a API já fornece os dados.
- Os documentos-base `09`, `11` e `13` não foram alterados. Este ADR registra a extensão até a revisão editorial deles.

## Evidências

- `apps/backend/tests/test_integration_session_lifecycle.py` (6 testes) cobre tempo registrado, indicadores só para admin, janela de renovação, limite, auditoria, sessão expirada e prazo estendido sem expiração indevida.
- Playwright local:
  - com 4 minutos restantes aparece o aviso, e "Renovar" leva o prazo a 15:00;
  - o banco registra `renewals=1` e `provision_ms`;
  - o endpoint de indicadores retorna p50/p95.
