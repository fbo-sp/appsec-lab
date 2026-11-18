# ADR-018: LAB-000 vira o tutorial da plataforma

- **Status:** Aceito pelo PO (2026-11-15).
- **Data:** 2026-11-15
- **Relacionados:** ADR-009 (workspace), ADR-010 (validação), ADR-013 (dicas), ADR-016, ADR-017

## Contexto

O LAB-000 nasceu como laboratório benigno para homologar o motor e "não deveria ser publicado para alunos". O PO pediu (2026-11-15) que ele seja transformado, sem ser refeito, num tutorial geral que ensine como a plataforma de laboratórios funciona.

## Decisão

1. **LAB-000 1.0.0 = tutorial.** Mesma imagem e mesmo runtime (servidor estático, sem vulnerabilidade), com narrativa de aluno em primeiro contato e cinco etapas, uma por parte da tela:
   1. conhecer a tela (painel, trilha, abas, prazo, progresso salvo), com o código mostrado na aba Aplicação;
   2. usar a barra de endereço, abrindo `/tutorial/endereco.html`, página sem link;
   3. usar o terminal (`whoami`, menor privilégio), reaproveitando o validador existente;
   4. pedir uma dica, cuja resposta está na dica 1 gratuita, explicando os custos do ADR-013;
   5. editar `index.html` e validar, reaproveitando o validador HTTP existente, explicando a validação em cópia isolada, a aba Validação, o resumo e o encerramento.
2. **Novos validadores de resposta:** `tutorial/answer/codigo-etapa-1-v1`, `tutorial/answer/codigo-etapa-2-v1` e `tutorial/answer/palavra-dica-v1`.
3. **Marcador de tutorial:** o contrato exige uma CWE principal; o tutorial mantém CWE-1000 (raiz da visão "Research Concepts"). O portal trata CWE-1000 como "sem vulnerabilidade": no painel aparece a etiqueta "Comece por aqui", e a página de abertura não mostra o bloco de classificação. No catálogo, o tutorial abre o arquivo, fora da tabela de classificação.
4. **Testes do motor:** a versão 0.2.1 fica congelada em `apps/backend/tests/fixtures/lab000-engine-0.2.1.yaml` e continua sendo a fixture dos testes de integração, que não dependem do texto do tutorial. Os testes Docker seguem usando o runtime do LAB-000; a página inicial continua com um único `</h1>` e sem "Olá, CECyber".

## Consequências

- O tutorial aparece primeiro no painel (ordem por id) e é indicado como primeira atividade de qualquer turma.
- Mudanças futuras na interface devem atualizar o texto do tutorial, com versão nova.
- Se surgir outro lab sem vulnerabilidade, vale trocar o marcador CWE-1000 por um campo próprio no manifesto.

## Adendo: ilustrações da interface (2026-11-15)

O PO pediu pequenas visualizações que exemplifiquem o texto das etapas. O Markdown restrito (ADR-012) ganhou um único caso: um bloco cercado com a linguagem `ilustracao` e um **nome de uma lista fixa** (`tela`, `barra-endereco`, `terminal`, `dicas`, `editar-validar`) é desenhado pelo portal com elementos React e CSS, sem imagens nem conteúdo externo. Um nome desconhecido continua aparecendo como bloco de código, então o manifesto não consegue injetar nada. Novos desenhos exigem mudança no portal (`apps/web/src/portal/Illustrations.tsx`).

**Adendo (2026-11-16, primeira leva).** A pedido do PO ("quando achar necessário, inclua visualizações nas explicações dos passos"), a lista fixa ganhou diagramas conceituais genéricos, reutilizados por todos os ramos de uma família (ADR-021): `xss-lista-bloqueio`, `xss-refletido`, `xss-armazenado`, `xss-codificacao-saida`, `mass-assignment` e `lista-permissao-campos`. A regra não muda: o manifesto só escolhe o nome, e o desenho e a legenda ficam no portal.
Ainda na primeira leva, para CSRF: `site-vs-origem`, `csrf-fluxo` e `csrf-token`.
