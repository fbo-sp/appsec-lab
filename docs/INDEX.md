# Índice e Estado da Documentação | CECyber AppSec Labs

**Data:** 2026-11-11. **Versão documental geral:** 0.3.0. **Estado:** planejamento, nenhuma arquitetura ou especificação formalmente aprovada.

| Documento | Estado |
|---|---|
| 00_PRODUCT_VISION.md | Rascunho detalhado, atualizado v0.3 |
| 01_PROJECT_CHARTER.md | Estrutura inicial |
| 02_PRD.md | Rascunho detalhado com adendo pedagógico |
| 03_FUNCTIONAL_REQUIREMENTS.md | Estrutura inicial + referência LEX |
| 04_NON_FUNCTIONAL_REQUIREMENTS.md | Estrutura inicial |
| 05_USER_JOURNEYS.md | Estrutura inicial |
| 06_SYSTEM_ARCHITECTURE.md | Proposta técnica v0.2 + on-prem e steps |
| 07_THREAT_MODEL.md | Proposta técnica v0.2, precisa revisar ambiente on-prem |
| 08_LAB_ENGINE_SPEC.md | Proposta técnica v0.2, precisa detalhar step lifecycle |
| 09_PROVISIONING_SPEC.md | Proposta técnica v0.2 + adendo on-prem |
| 10_VALIDATION_ENGINE_SPEC.md | Proposta técnica v0.2 + validação por etapa |
| 11_LAB_MANIFEST_SPEC.md | Especificação proposta v0.3 detalhada |
| 12_DATA_MODEL.md | Modelo lógico proposto v0.3 |
| 13_API_SPEC.md | Contrato REST inicial v0.3; OpenAPI formal pendente |
| 14_MVP_SCOPE.md | Escopo proposto v0.3 |
| 15_PRODUCT_BACKLOG.md | Backlog inicial + histórias US-031 a US-039 |
| 16_TEST_STRATEGY.md | Estrutura inicial |
| 17_MVP_LAB_CATALOG.md | Estrutura inicial + padrão editorial |
| 18_RELEASE_PLAN.md | Estrutura inicial |
| 19_OPERATIONS_RUNBOOK.md | Estrutura inicial |
| 20_RISKS_AND_DECISIONS.md | Estrutura inicial |
| 21_LEARNING_EXPERIENCE_SPEC.md | Novo: seis princípios pedagógicos e aceite |
| ADR/ADR-001-runtime.md | Proposta, PoC pendente |
| ADR/ADR-002-isolation.md | Proposta, PoC pendente |
| ADR/ADR-003-validation.md | Proposta, PoC pendente |
| ADR/ADR-004-on-premises-hosting.md | Decisão de produto on-prem; topologia em avaliação |
| 22_PROJECT_INITIAL_ASSESSMENT.md | Novo (2026-11-11): diagnóstico, lacunas G-01–G-19, riscos |
| 23_IMPLEMENTATION_PLAN.md | Novo: fases F0–F6, vertical slice, estratégias local/on-prem |
| 24_IMPLEMENTATION_BACKLOG.md | Novo: backlog executável IMP-xxx |
| 25_DEVELOPMENT_STATUS.md | Novo: status para continuidade entre sessões de IA |
| ADR/ADR-005-academic-model.md | Aprovado (2026-11-11): LabAttempt/StepSubmission/ValidationRun |
| ADR/ADR-006-manifest-contract-v1alpha1.md | Aprovado (2026-11-11), implementado |
| ADR/ADR-007-postgres-job-queue.md | Aprovado (2026-11-11), implementado |
| ADR/ADR-008-local-docker-runtime.md | Aprovado (2026-11-12), implementado (somente local/test) |
| ADR/ADR-009-local-workspace-gateway.md | Proposto; implementado só local/test (2026-11-12) |

## Ordem recomendada para trabalho com agentes

1. Revisar PRD e LEX (passo a passo, validação, variantes).
2. Fazer inventário e PoC on-premises, incluindo isolamento e capacidade.
3. Formalizar manifesto v1, esquema de dados e OpenAPI com testes de contrato.
4. Atualizar motor e validadores para desbloqueio transacional por etapa.
5. Implementar os quatro labs com storytelling e aplicações realistas.
6. Testar adversarialmente o sandbox, revisar documentação de operação e liberar piloto por gate.
