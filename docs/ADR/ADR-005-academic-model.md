# ADR-005: Modelo acadêmico — LabAttempt, StepSubmission e ValidationRun

- **Status:** Proposto, **aguardando decisão do PO/Acadêmico**
- **Data:** 2026-11-11
- **Contexto de origem:** `22_PROJECT_INITIAL_ASSESSMENT.md` G-02

## Contexto

O termo "Attempt" tem dois significados nos documentos: *submissão para avaliação* (PRD §4, `10`, `12` como `step_attempts`) e *tentativa de resolução do laboratório* ("Laboratory Attempt", na diretriz do PO). Além disso, `12` vincula `step_progress` à **sessão**, o que conflita com "progresso acadêmico ≠ estado do runtime" (Visão §8, BR-005) e com `policy.persistProgressAcrossReset`: se a sessão expira, o progresso ficaria preso a um recurso efêmero.

## Decisão proposta

| Conceito | Entidade | Ciclo de vida |
|---|---|---|
| Laboratory | `labs` | Estável |
| Laboratory Version | `lab_releases` (sinônimo de LaboratoryVersion) | Imutável após publicada |
| Laboratory Variant | `lab_variants` | Parte da release |
| Laboratory Step | `lab_steps` | Parte da release |
| **Laboratory Attempt** | `lab_attempts` (user, release, variant, status, score, started/completed) | Durável; dono do progresso |
| Laboratory Session | `lab_sessions` → FK `attempt_id` | Efêmera; N sessões por attempt |
| Step progress | `step_progress` (attempt, step, status LOCKED/AVAILABLE/IN_PROGRESS/PASSED) | Durável |
| Step submission | `step_submissions` (attempt, session, step, snapshot_digest, idempotency_key) | Imutável |
| Validation Run | `validation_runs` (submission, suite_digest, status interno de `10 §7`) | Imutável ao concluir |
| Validation Result | `criterion_results` + projeção pública (`QUEUED/RUNNING/PASSED/FAILED/ERROR`) | Imutável |

Regras: nova sessão para o mesmo attempt continua o progresso (política padrão; "reiniciar roteiro" cria novo attempt). Desbloqueio de etapa e commit do resultado aprovado na mesma transação.

## Consequências

+ Progresso sobrevive a reset, expiração e destruição do runtime.
+ Terminologia alinhada ao pedido do PO e ao PRD.
- Renomeia `step_attempts` de `12` para `step_submissions` (documento 12 precisa de revisão).

## Pendências

Política de "continuar vs. reiniciar" (`21 §3`), número máximo de attempts e regra de nota consolidada (FR-048, OPEN-04).
