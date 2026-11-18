# ADR-019: Tarefa enxuta e estudo complementar opcional ("Explorar mais")

- **Status:** Aceito pelo PO (2026-11-15).
- **Data:** 2026-11-15
- **Relacionados:** ADR-012 (conteúdo rico), ADR-013 (dicas), ADR-018

## Contexto

Ao testar o LAB-003, o PO notou que o texto da tarefa misturava a instrução necessária para concluir a etapa com verificações complementares (ler `/tmp/app.log`, conferir o pior caso, solucionar problemas). Isso confundia o aluno: ele rodava um `tail` e ia procurar no log uma resposta que não estava ali, ou procurava um erro que ainda não existia porque ainda não tinha clicado em **Validar**. Em uma etapa, "saia e entre de novo na aba Aplicação" não deixava claro que era preciso deslogar e relogar com as credenciais da própria história.

## Decisão

1. **A tarefa traz só o necessário para concluir a etapa.** O campo `steps[].task` descreve apenas os passos que levam à resposta ou à correção pedida. Nada de leitura de log, pior caso ou solução de problemas no fluxo principal.
2. **Estudo complementar em `steps[].explore`.** Campo opcional (Markdown restrito, ADR-012) com o que antes poluía a tarefa. Aparece atrás de um botão **Explorar mais** na etapa, que abre um modal (como o de dicas). Não vale pontos e não é preciso para concluir a etapa.
3. **O complemento explica o valor, não só o comando.** Cada `explore` diz **por que** vale abrir o log ou fazer a exploração e **que tipo de achado** pode surgir (por exemplo: o log atribui a fraude a uma cliente comum; a enumeração também expõe um PIX de valor alto). O aluno precisa entender o valor, não decorar o comando.
4. **Relogin explícito.** Quando a etapa pede para autenticar de novo, o texto diz para clicar em **Sair** e logar outra vez com as credenciais, repetindo-as e lembrando que estão na etapa 1.
5. **Padrão para todos os labs.** Revisão aplicada ao LAB-001, LAB-002, LAB-003 e LAB-004; o tutorial LAB-000 ganha um `explore` de exemplo para apresentar o recurso. Novos labs já nascem nesse padrão.

## Consequências

- Contrato: `LabStep` ganha `explore: NonEmptyText | None = None`, opcional e sem default serializado, de modo que os digests das releases existentes não mudam. Schema reexportado.
- Backend: `progress/service.py` repassa `explore` na visão da etapa; frontend expõe o botão e o modal `ExploreModal` em `StepPanel.tsx`.
- Versões novas: LAB-000 1.0.1, LAB-001 1.0.3, LAB-002 1.0.3, LAB-003 1.0.2, LAB-004 1.0.3, com histórico e catálogo regenerados.
- O catálogo mostra só o título das etapas, então o `explore` não aparece nele; é conteúdo de tela.
