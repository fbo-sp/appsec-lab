# 15. Backlog Inicial do Produto

| Campo | Valor |
|---|---|
| Versão | 0.1.0 |
| Estado | Sementes de backlog para refinamento, **não estimadas** |
| Fonte | `02_PRD.md` |

## Políticas

- P0 é obrigatório para piloto; P1 negociável; P2 pós-MVP.
- Cada história deverá ter aceite Given/When/Then, teste automatizado, dependência, dono, estimativa e link FR/NFR.
- Não iniciar histórias que executem código não confiável sem decisões de isolamento aprovadas.

## Backlog de épicos e histórias iniciais

| Épico | História inicial | Prioridade | Requisitos | Gate / dependência |
|---|---|---|---|---|
| EP01 Identidade | US-001 Autenticar usuário via OIDC | P0 | FR-001 | Escolha IdP |
| EP01 Identidade | US-002 Autorizar sessão por ownership | P0 | FR-002, NFR-014 | Threat model |
| EP01 Identidade | US-003 Atribuir lab à turma | P0 | FR-004 | Modelo de turmas |
| EP02 Catálogo | US-004 Validar manifesto e versão | P0 | FR-011 | Schema v1 |
| EP02 Catálogo | US-005 Listar lab publicado/autorizado | P0 | FR-010 | US-003 |
| EP02 Catálogo | US-006 Publicar artefato versionado | P0 | FR-012/013 | Pipeline |
| EP03 Sessões | US-007 Criar sessão idempotente | P0 | FR-020/022 | Modelo de estados |
| EP03 Sessões | US-008 Consultar/reconectar sessão | P0 | FR-023 | US-007 |
| EP03 Sessões | US-009 Reset e TTL de sessão | P0 | FR-024/025 | Políticas de retenção |
| EP03 Sessões | US-010 Reconciliar recursos órfãos | P0 | FR-026 | PoC runtime |
| EP04 Provisionamento | US-011 Provisionar sandbox por adapter | P0 | FR-020, NFR-001 | ADR isolamento |
| EP04 Provisionamento | US-012 Impor quotas e egress deny | P0 | FR-027, NFR-002 | ADR runtime |
| EP05 Workspace | US-013 Editar arquivos autorizados | P0 | FR-031 | Gateway |
| EP05 Workspace | US-014 Terminal WebSocket autenticado | P0 | FR-032 | US-002, US-011 |
| EP05 Workspace | US-015 Prévia web autorizada | P0 | FR-033 | Anti-SSRF |
| EP06 Validação | US-016 Snapshot estável da tentativa | P0 | FR-040/041 | Modelo de workspace |
| EP06 Validação | US-017 Rodar suite protegida | P0 | FR-042/043 | ADR validação |
| EP06 Validação | US-018 Nota e feedback auditáveis | P0 | FR-044/045/046 | US-017 |
| EP06 Validação | US-019 Bloquear avaliações concorrentes | P0 | FR-047 | US-016 |
| EP07 Gestão | US-020 Visão de progresso por turma | P0 | FR-050 | Resultados persistidos |
| EP07 Gestão | US-021 Exportar CSV filtrado | P0 | FR-051 | Política dados |
| EP08 Conteúdo | US-022 Publicar LAB-001 SQLi | P0 | LAB-001 | Engine + validator |
| EP08 Conteúdo | US-023 Publicar LAB-002 IDOR | P0 | LAB-002 | Engine + validator |
| EP08 Conteúdo | US-024 Publicar LAB-003 JWT | P0 | LAB-003 | Segundo runtime |
| EP08 Conteúdo | US-025 Publicar LAB-004 Command Injection | P0 condicionado | LAB-004 | Gate contenção |
| EP09 Segurança | US-026 Testar isolamento e abuso do gateway | P0 | NFR-001/002/014 | Infra de teste |
| EP10 Operação | US-027 Métricas, auditoria e cleanup | P0 | FR-053, NFR-007/010 | Base de eventos |
| EP13 DevEx | US-028 Pipeline de publicação e smoke tests | P0 | FR-013, NFR-012 | Registry |
| EP12 Integração | US-029 API de resultados versionada | P1 | FR-054 | Contrato LMS |
| EP11 Relatórios | US-030 Indicadores acadêmicos adicionais | P1 | FR-050 | Feedback piloto |

## Próximas atividades

1. Refinar as histórias de risco alto (US-002, US-007, US-011, US-017, US-026).
2. Transformar critérios do PRD em testes e contratos executáveis.
3. Estimar esforço depois das quatro PoCs.
4. Planejar sprints de forma incremental, com segurança e observabilidade em todos eles.

## Incremento v0.3: backlog obrigatório de experiência didática/on-premises

| ID | História | Prioridade | Dependência | Aceite resumido |
|---|---|---|---|---|
| US-031 | Exibir storytelling, CWE e aplicação realista | P0 | Manifest v1 | 4 labs com contexto antes do início |
| US-032 | Garantir uma CWE principal por lab | P0 | Curadoria de conteúdo | Checagem de publicação e revisão |
| US-033 | Exibir passo atual e conceitos com progressão sequencial | P0 | Dados e API de steps | Etapa posterior bloqueada no backend |
| US-034 | Criar hints em níveis com rastreamento | P0 | StepHint e API | Dicas graduais auditáveis |
| US-035 | Avaliar cada passo e desbloquear o seguinte atomicamente | P0 | Runner + banco | Sem avanço por evento falso do cliente |
| US-036 | Editar, salvar, compilar/precompilar/interpretar e executar | P0 | Gateway/runtime profile | Python e Node.js via comandos aprovados |
| US-037 | Implementar contrato de variantes por linguagem | P0 | Manifesto e modelo | Mesmo lab, duas variantes mapeiam passos iguais |
| US-038 | Validar topologia on-premises, segregação e capacidade | P0 | ADR-004 e inventário | PoCs de 30 sessões e testes de isolamento |
| US-039 | Publicar segundo idioma/runtime de um mesmo lab | P1 | US-037 | Sem alteração no motor |

**Prioridade de implementação:** US-038 + US-035 e contratos de manifestos/dados antes do portal completo. Nenhuma capacidade nova deve furar o gate de isolamento.
