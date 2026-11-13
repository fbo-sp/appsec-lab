# ADR-014: Tempo de sessão, tempo de resolução e encerramento de sessões paradas

- **Status:** Aprovado pelo PO em 2026-11-13; implementado (2026-11-13). Só local/test, como os ADR-008 a 011.
- **Data:** 2026-11-13
- **Relacionados:** ADR-011 (renovação e indicadores de provisionamento), ADR-009 (gateway), ADR-013, IMP-205 (quotas)

## Contexto

Ao testar o LAB-001, o PO encerrou e reiniciou sessões. Cada sessão nova recebe o prazo inteiro (45 min), o que é o comportamento esperado, mas a experiência confundia. O PO definiu dois indicadores com finalidades diferentes:

- **tempo de sessão**, base de provisionamento e cálculo de capacidade;
- **tempo de resolução do laboratório**, base para dimensionar o curso, sem contar tempo parado.

Também pediu encerrar sessões paradas para economizar recursos.

## Decisão

1. **Prazo por sessão (mantido).** Cada sessão tem `ttlMinutes` e suas renovações. O progresso fica na tentativa. Ao abrir uma sessão nova de uma tentativa já iniciada, o portal avisa "Nova sessão de N min. Seu progresso foi mantido". O botão de renovação mostra "(1 de 2)".
2. **Tempo de sessão.** `lab_sessions.ended_at` e `end_reason` são gravados na primeira saída de um estado vivo:
   - motivos: `request_termination` (aluno ou admin), `expire`, `fail`, `complete` e `idle`;
   - a expiração conta até o prazo, não até o instante em que o worker a detecta;
   - tempo de uso = `ended_at − ready_at`, inclusive tempo ocioso, porque o ambiente ocupa recursos do mesmo jeito.
   - `GET /api/v1/admin/metrics/provisioning` passa a incluir `usageMinutes` (média, p50, p95, máximo) e `endReasons`.
3. **Atividade.** Contam como atividade do aluno:
   - no gateway: requisições à aplicação do lab, chamadas da API de arquivos do workspace e digitação no terminal (mensagens do cliente, não pings do WebSocket), gravadas no máximo uma vez a cada 30 s por sessão;
   - na API: validar, abrir dica e renovar;
   - no portal: clique, tecla ou rolagem no portal ou no workspace (que avisa o portal por `postMessage` sem dados), com a aba visível, enviados no máximo uma vez por minuto (`POST /sessions/{id}/activity`).
   Ter a aba aberta não conta. A atividade grava `lab_sessions.last_activity_at` e um registro por minuto em `attempt_activity`.
4. **Encerramento por inatividade.** O reconciliador encerra sessões prontas sem atividade há `SESSION_IDLE_MINUTES` (padrão 15; 0 desativa), com motivo `idle` na auditoria e em `end_reason`. Três minutos antes, o portal mostra "Você ainda está aí?" com "Continuar trabalhando". O ambiente é removido e o progresso fica salvo.
5. **Tempo de resolução.** Minutos distintos com atividade na tentativa, somando todas as sessões, até a conclusão.
   - O resumo de conclusão mostra "N min de trabalho ativo em K sessões". O tempo de calendário aparece só como dica.
   - `GET /api/v1/admin/metrics/resolution?days=30` (só admin) devolve, por laboratório e versão: tentativas concluídas, minutos ativos (média, p50, p90), p50 do tempo de calendário e sessões por tentativa.

## Consequências

- Migração `0005`: `ended_at`, `end_reason` e `last_activity_at` em `lab_sessions`; tabela `attempt_activity` (chave `attempt_id` + `minute`). Sessões antigas recebem `ended_at` aproximado (`updated_at`, limitado ao prazo).
- Leitura sem interação (por exemplo, ler o enunciado por mais de 15 minutos sem rolar) pode encerrar a sessão; o aviso de 3 minutos mitiga. O limite é configurável.
- Encerrar e iniciar de novo continua dando um prazo novo; isso não é problema enquanto o prazo servir para liberar recursos. Um orçamento de tempo por aluno ou organização fica para IMP-205 (quotas).
- Minutos ativos por etapa ficam para depois; os dados já permitem calcular.
- Em produção, o sinal do gateway e do portal precisa ser revisto junto com o ADR-003 (runner de produção).

## Evidências

- `test_integration_session_lifecycle.py`: fim e motivo da sessão, indicadores de uso, inatividade adiada por atividade e encerrada após o limite, minutos ativos distintos entre sessões.
- `test_integration_progress.py`: indicador de resolução usa minutos ativos.
- `test_unit_gateway.py`: atividade do gateway com limite de frequência e só com grant válido.
- Playwright local com `SESSION_IDLE_MINUTES=4`: aviso após 1 min parado, "Continuar trabalhando" adia, e sem interação a sessão é encerrada com a mensagem de inatividade.
