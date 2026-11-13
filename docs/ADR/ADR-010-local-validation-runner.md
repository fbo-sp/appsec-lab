# ADR-010: Avaliação de etapas fora do workspace (runner local)

- **Status:** Proposto, implementado só para local/test (2026-11-12). **Não decide o ADR-003**, que segue pendente de PoC para produção.
- **Data:** 2026-11-12
- **Relacionados:** ADR-003 (runner protegido, pendente), ADR-005 (modelo acadêmico), ADR-008 (runtime Docker local), ADR-009 (gateway), `21` (experiência), OPEN-04, IMP-401–405

## Contexto

A experiência exige validar cada etapa e liberar a próxima no servidor (`21`, `13 §3`). O requisito do PO é que "os validadores protegidos executem fora do workspace editável pelo aluno". O ADR-003 (runner de produção) ainda não tem PoC. Para que o aluno consiga testar o LAB-000 e o LAB-001 **localmente**, precisamos de um mecanismo provisório que já respeite as regras de segurança essenciais.

## Decisão

1. **Registro protegido de validadores** (`app/validation/suites.py`):
   - código versionado no plano de controle; o manifesto só referencia `validatorRef`;
   - o catálogo recusa referências desconhecidas (`UNKNOWN_VALIDATOR`, regra 6 de `11 §3`);
   - critérios, respostas aceitas e verificações **nunca** são enviados ao navegador nem ao contêiner do aluno;
   - cada submissão grava `validator_ref` e `suite_digest`, o que permite auditar com qual versão foi avaliada.
2. **Dois tipos de verificação**:
   - `answer`: a resposta do aluno é normalizada e comparada **na API**;
   - `http` (comportamental): um job `EVALUATE` é executado pelo worker.
3. **Avaliação comportamental (DockerEvaluator, só local/test)**:
   1. Snapshot do workspace do contêiner da sessão (`get_archive`, limite de 20 MiB, digest registrado). Links simbólicos, dispositivos e caminhos fora do workspace são descartados.
   2. Um contêiner **novo** é criado a partir da mesma imagem, com o snapshot num volume próprio e o mesmo endurecimento do ADR-008 (não-root, raiz somente leitura, `cap_drop=ALL`, limites). Ele fica numa rede `internal` exclusiva e executa **só a aplicação**: o agente de workspace não roda.
   3. Um probe confiável (`probe.py`, só stdlib, sem segredos, sem socket, sem portas) roda em contêiner efêmero nessa rede, faz as requisições da suíte e devolve um resultado por critério.
   4. A limpeza de contêineres, rede e volume é garantida (`finally`), e os recursos são rotulados por submissão.
4. **Fail closed**: com runtime fake, avaliador ausente, exceção ou timeout, o resultado é `ERROR` com mensagem técnica. Isso **nunca** aprova nem reprova o aluno, e a etapa continua disponível.
5. **Progresso transacional** (ADR-005):
   - aprovação, pontos, desbloqueio da próxima etapa e conclusão da tentativa ocorrem na mesma transação;
   - há uma avaliação pendente por sessão e idempotência por `Idempotency-Key`;
   - o progresso pertence à tentativa e sobrevive ao fim da sessão.
6. **OPEN-04** (PO, 2026-11-12): dicas são reveladas em ordem e as tentativas são ilimitadas. O desconto por dicas foi revisto pelo PO em 2026-11-13 e agora segue o ADR-013 (custo por nível, teto de 10%). Tudo é auditado (`step.submitted`, `step.passed|failed|error`, `hint.revealed`, `attempt.completed`).

## Alternativas consideradas

- **Rodar testes dentro do contêiner do aluno:** rejeitada, porque o aluno controla esse ambiente e poderia forjar o resultado.
- **Testar a instância viva do aluno pela rede:** é mais simples, mas o aluno pode alterar o estado durante a avaliação, e o teste não seria reprodutível. O snapshot dá consistência e um digest para auditoria.
- **Envelope assinado entre o runner e a API (IMP-403):** é desnecessário enquanto o runner é o próprio worker confiável. Volta a ser exigido quando o runner for um serviço separado (ADR-003).

### Adendo (2026-11-13): aplicação que não inicia

Se a cópia avaliada não responder dentro da espera do probe (30 s), a avaliação não lista as N verificações da suíte como falhas de segurança. Ela reprova com um único critério, "A aplicação inicia com o código salvo", e o feedback traz as últimas linhas da saída da aplicação (por exemplo, um `IndentationError`), tratadas como dado não confiável e mostradas como texto. Recursos de avaliação (rótulo `evaluation-id`) só são considerados órfãos pelo reconciliador após 10 minutos.

## Consequências e limitações

- O worker local precisa do socket Docker, que já era necessário no ADR-008. Isso **não serve para produção**.
- A aplicação do aluno ainda pode "enganar" verificações caixa-preta (por exemplo, respondendo exatamente o texto esperado). As suítes do LAB-001 em diante devem combinar verificações de exploração e de funcionalidade (positivas e negativas).
- Cada avaliação comportamental leva alguns segundos (criação de contêiner e espera da aplicação).
- Não há rate limit de submissões. Tentativas ilimitadas (OPEN-04) também valem para carga, e o limite operacional fica para IMP-205.

## Evidências

- `apps/backend/tests/test_integration_progress.py` (19 testes) cobre desbloqueio, idempotência, etapa bloqueada, ordem de dicas, tentativas livres, os caminhos `http` e `ERROR`, e o progresso entre sessões.
- `apps/backend/tests/test_docker_evaluator.py` (4 testes com Docker real, opt-in) cobre snapshot, cópia isolada, critérios, link simbólico descartado, aplicação que não sobe, limpeza e runtime inexistente.
- O fluxo Playwright no portal local está registrado em `docs/25`.
