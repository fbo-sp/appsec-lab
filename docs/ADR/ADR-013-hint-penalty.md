# ADR-013: Desconto por uso de dicas (substitui a parte de dicas do OPEN-04)

- **Status:** Aprovado pelo PO em 2026-11-13 (cards de decisão); implementado (2026-11-13).
- **Data:** 2026-11-13
- **Relacionados:** ADR-010 (decisão 6, OPEN-04), `docs/10_VALIDATION_ENGINE_SPEC.md`, `docs/21_LEARNING_EXPERIENCE_SPEC.md`, IMP-405

## Contexto

Em 2026-11-12 o PO decidiu que dicas não descontariam pontos (OPEN-04). Depois de testar o LAB-001, o PO pediu desconto por uso de dicas, com duas restrições: o desconto total não pode passar de 10% da pontuação e os valores devem ser inteiros.

## Decisão

1. **Custo por nível.** A dica 1 é grátis, a dica 2 custa 1 ponto e a dica 3 (ou posterior, que quase entrega a resposta) custa 2 pontos. Revelar de novo uma dica já vista não cobra outra vez.
2. **Teto.** O desconto da tentativa é `min(piso(10% × pontuação máxima), soma dos custos)`. Com 100 pontos, o teto é 10. A pontuação da tentativa é `pontos das etapas aprovadas − desconto`, nunca negativa. Os pontos de cada etapa não mudam.
3. **Aprovação.** A conclusão do laboratório continua dependendo só de todas as etapas aprovadas. O desconto reduz a nota mostrada e registrada, mas não reprova. `policy.finalPassingScore` não é usado para concluir a tentativa.
4. **Regra da plataforma, sem campo no manifesto.** Vale para todas as releases, inclusive as já publicadas, sem novas versões. Um custo configurável por laboratório fica para quando houver necessidade.
5. **Transparência.** O portal mostra o custo antes de revelar ("Revelar dica 2 (−1 pt)"), o custo de cada dica revelada, o desconto ao lado do placar ("· dicas −3") e no resumo final. A API expõe `attempt.earnedPoints`, `attempt.hintPenalty`, `attempt.hintPenaltyCap`, `hints.revealed[].cost` e `hints.nextCost` (custo efetivo, 0 quando o teto já foi atingido). `reveal` devolve o desconto aplicado (`penalty`) e a pontuação atualizada.
6. **Auditoria.** O evento `hint.revealed` registra o desconto aplicado (`metadata.penalty`).

## Consequências

- Implementado em `apps/backend/app/progress/service.py` (`hint_cost`, `hint_penalty`, `_recompute_score`), com testes unitários e de integração.
- Tentativas anteriores ao ADR mantêm a pontuação gravada até a próxima dica revelada ou etapa aprovada, quando a pontuação é recalculada. Isso só afeta ambientes locais de teste.
- Labs muito pequenos (menos de 10 pontos) têm teto 0, ou seja, sem desconto.
