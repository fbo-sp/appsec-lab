# ADR-020: Selo de laboratório concluído no painel

- **Status:** Proposto (2026-11-15). Regra de versão aguardando confirmação do PO.
- **Data:** 2026-11-15
- **Relacionados:** ADR-005 (tentativa dona do progresso), ADR-013 (pontuação com dicas), ADR-016 (painel só com a última versão)

## Contexto

O PO pediu que os cards do painel mostrem se o aluno já concluiu o laboratório alguma vez. A tentativa (`lab_attempts`) já guarda `status`, `score` e `completed_at`, e a conclusão é decidida no servidor quando a última etapa é aprovada. Como o painel lista só a versão mais alta de cada lab (ADR-016), uma conclusão em versão anterior sumiria se o selo considerasse apenas a versão listada.

## Decisão

1. **Endpoint próprio do usuário:** `GET /api/v1/me/lab-completions` devolve, por laboratório, as versões concluídas pelo usuário autenticado (da mais nova para a mais antiga) com `completedAttempts`, `bestScore`, `maxScore`, `firstCompletedAt` e `lastCompletedAt`. O dono vem sempre do principal, nunca de parâmetro. O catálogo (`/labs`) continua sem dados por usuário, para não misturar conteúdo publicado com progresso.
2. **Só tentativas `COMPLETED`:** tentativa em andamento não conta. A pontuação é a líquida (com desconto de dicas, ADR-013); desconto não impede a conclusão.
3. **Regra de versão (recomendada, pendente do PO):** o selo vale para qualquer versão. Se a versão listada foi concluída, o card mostra **Concluído**; se só uma versão anterior foi, mostra **Concluído na versão X** em cor neutra. Abaixo, a melhor pontuação e a data da última conclusão (e "N vezes" quando houver mais de uma).
4. **Falha não bloqueia o painel:** se a consulta falhar, os cards aparecem sem selo.

## Consequências

- Nenhuma migração: consulta agregada sobre `lab_attempts` + `lab_releases`.
- Não expõe respostas, dicas nem detalhes de etapas.
- Se o PO preferir "só a versão atual", basta o frontend ignorar as versões anteriores; o contrato da API não muda.
- Escopo por turma/atribuição (IMP-204) e visão do instrutor seguem fora desta mudança.
