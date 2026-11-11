# 21. Experiência Pedagógica e Progressão dos Laboratórios

| Campo | Valor |
|---|---|
| Produto | CECyber AppSec Labs |
| Versão | 0.3.0 |
| Estado | Requisitos priorizados a partir de feedback do Product Owner |
| Prioridade | P0 para os seis princípios; múltiplas variantes publicadas é P1 |

## 1. Seis princípios obrigatórios

**LEX-001 Storytelling contextualizado (P0).** Antes de iniciar, apresentar o contexto do incidente/problema, a empresa fictícia, o papel do aluno, a aplicação realista que será iniciada, a vulnerabilidade e a CWE principal (mais CWEs complementares quando justificadas). Evitar entregar a exploração exata antes do exercício.

**LEX-002 Uma vulnerabilidade por laboratório (P0).** Cada lab tem um único objetivo técnico principal e uma CWE principal; vulnerabilidades auxiliares não devem competir pedagogicamente. Labs separados para conceitos distintos; passo de correção deve referenciar a mesma vulnerabilidade investigada.

**LEX-003 Aprendizagem guiada passo a passo (P0).** Cada etapa inclui título, explicação do que ocorre, tarefa concreta, conceito relevante, resultado esperado e feedback. O aluno tem visibilidade do progresso e dos passos completados; conteúdo da próxima etapa só é revelado quando liberado.

**LEX-004 Código realista e ciclo de desenvolvimento (P0).** Disponibilizar projeto com pastas, serviços e responsabilidades plausíveis. UI com editor, arquivos, terminal, preview, salvar, executar e compilar/pré-compilar/interpretar conforme a linguagem. O código inseguro deve ser suficientemente pequeno para um exercício curto, mas não artificialmente reduzido a uma linha solta.

**LEX-005 Validação e desbloqueio individual (P0).** Cada etapa possui pelo menos um critério automaticamente verificável, com serviço confiável independente do aluno. Etapa seguinte inicialmente `LOCKED`, apenas backend pode torná-la `AVAILABLE` após avaliação `PASSED`. Dicas escalonadas em 2 a 3 níveis podem apontar arquivo ou linha aproximada; uso e efeito em pontos devem ser registrados. Erro do validador não equivale a reprovação e não avança a etapa.

**LEX-006 Linguagens por variante (P0 no modelo, P1 na oferta).** Uma definição conceitual de laboratório pode ter variantes de linguagem/framework e validadores independentes, preservando narrativa, objetivos, ordem e critérios de sucesso. O MVP deve provar o suporte de esquema/API; oferecer a mesma vulnerabilidade em duas linguagens pode ser exercício de homologação, não requisito de catálogo completo.

## 2. Jornada do aluno

1. Catálogo: escolher laboratório e linguagem disponível.
2. Introdução: compreender cenário, alvo autorizado, CWE, resultados e pré-requisitos.
3. Iniciar: criar sessão da variante, com ambiente isolado.
4. Etapa atual: ler contexto, conceito, instrução e objetivo verificável.
5. Investigar: editor de arquivos, terminal, build/run e aplicação funcional.
6. Solicitar dica: liberar próximo nível e registrar uso.
7. Verificar: enviar submissão; receber `QUEUED/RUNNING/PASSED/FAILED/ERROR`.
8. Em `PASSED`, persistir evidência e liberar próxima etapa atomicamente.
9. Ao concluir, apresentar explicação final, pontos, referências e histórico.

## 3. Modelo de progresso

`LOCKED -> AVAILABLE -> IN_PROGRESS -> PASSED`; `FAILED` é resultado de tentativa, não estado final da etapa. `ERROR` indica problema de avaliação, permite retry sem penalização. Repetir sessão não apaga progresso acadêmico histórico; política sobre continuar de onde parou ou reiniciar o roteiro será configurável. Não confiar em evento enviado diretamente pelo navegador para indicar aprovação.

## 4. UX mínima

- Cabeçalho de progresso com etapa X/N, CWE e linguagem.
- Coluna didática com contexto, explicações, ação atual e dicas.
- Coluna de ambiente com árvore de arquivos, editor, terminal e preview de aplicação.
- Barra de ações: Salvar, Build/Run, Reiniciar, Solicitar dica, Validar etapa.
- Feedback inteligível, progresso persistido ao reconectar e mensagens claras de timeout/erro de runtime.
- Responsividade: experiência de programação prioriza desktop; mobile pode visualizar conteúdo, mas não precisa suportar edição avançada no MVP.

## 5. Exemplo de etapas do LAB-001

| Ordem | Etapa | O que aprende | Como valida |
|---|---|---|---|
| 1 | Compreender a aplicação | Fluxo controller -> repository -> database | Identificar ponto de construção insegura por interação verificável |
| 2 | Demonstrar a falha | Diferença entre dado e código em SQL | Verificador observa objetivo de exploração em dados fictícios |
| 3 | Implementar correção | Parametrização de consulta | Suite oculta verifica casos legítimos e maliciosos |
| 4 | Refletir | Causa raiz e prevenção | Quiz curto ou assertiva verificável, sem expor testes |

## 6. Critérios de aceite transversais

- Cenário, CWE, papel e aplicação existem nos quatro labs.
- Cada lab testa uma vulnerabilidade central, identificada em manifesto e revisão de conteúdo.
- Em todas as etapas, há explicação, tarefa, validação e desbloqueio pelo backend.
- Dicas de três níveis podem ser liberadas sem revelar informação futura.
- O aluno executa alteração de código e `build/run` em pelo menos um lab compilado/interpretado conforme seu runtime; Node.js e Python cobrem dois runtimes no MVP.
- Os validadores não são acessíveis pelo workspace do aluno.
- Duas variantes de um lab conseguem mapear às mesmas etapas mesmo usando imagens/testes distintos (teste de contrato).

## 7. Questões ainda abertas

Definir se a primeira dica é gratuita, se dicas afetam pontuação, quantas tentativas serão permitidas e se respostas finais completas podem ser reveladas após conclusão. Questões não bloqueiam arquitetura: armazenar policy declarativa e uma trilha auditável de hints.
