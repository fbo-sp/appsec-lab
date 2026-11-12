# ADR-006: Contrato implementado do manifesto AppSecLab v1alpha1

- **Status:** **Aprovado** pelo Product Owner em 2026-11-11 (PR #1); implementado na 1ª fatia
- **Data:** 2026-11-11
- **Contexto de origem:** `11_LAB_MANIFEST_SPEC.md`; `22` G-08, G-19

## Decisão

1. Fonte de verdade: modelos Pydantic em `packages/contracts/src/cecyber_contracts/manifest.py`; JSON Schema exportado em `packages/contracts/schemas/appseclab.v1alpha1.schema.json` com teste de drift.
2. `extra="forbid"` em todos os níveis: campos desconhecidos são rejeitados (inclui `privileged`, `hostPath` etc.).
3. **Estado de publicação não pertence ao manifesto**: `metadata.status` é rejeitado; o estado vive em `lab_releases.status` (o manifesto publicado é imutável).
4. Imagem obrigatoriamente por digest `sha256:<64 hex>`; tags e placeholders são rejeitados.
5. Comandos são listas de argumentos (sem string de shell).
6. Rede: somente `egressProfile: deny-all` (BR-009; OPEN-09 pendente).
7. Recursos e TTL são por variante, limitados pelos tetos do `runtimeProfile` server-side (`benign-test`, `web-basic`, `api-basic`, `exec-restricted` — este último **desabilitado** até ADR-002). Os nomes de perfil seguem `09 §7` (o exemplo `web-app` de `11` foi substituído).
8. Soma de `points` das etapas = 100; `finalPassingScore` ≤ soma (proposta para G-07, sujeita a OPEN-04).
9. Digest canônico: sha256 do JSON normalizado (chaves ordenadas), independente de formatação YAML.

## Pendente

Regra 6 de `11 §3` (existência do `validatorRef` no registro protegido) depende do ADR-003. Conteúdo em arquivos (`content/pt-BR/*.md`, `11 §4`) ainda não suportado no v1alpha1 implementado. Exigência de ≥3 etapas (gate G4) será regra de publicação de conteúdo, não do schema (o lab benigno de teste tem 1 etapa).
