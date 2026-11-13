# ADR-012: Conteúdo rico nas etapas (Markdown restrito, referências e "Para ir além")

- **Status:** Aprovado pelo PO em 2026-11-13; implementado (2026-11-13).
- **Data:** 2026-11-13
- **Relacionados:** ADR-006 (contrato do manifesto), `docs/21_LEARNING_EXPERIENCE_SPEC.md` §4–5, `docs/11_LAB_MANIFEST_SPEC.md`, IMP-501

## Contexto

O PO comparou o LAB-000 com laboratórios de mercado e pediu passos muito claros para alunos iniciantes: o porquê, o conceito, fontes e, quando preciso, a linha exata de código a mudar. Os campos da etapa (`explanation`, `task`, `concept`, dicas) eram texto simples, sem blocos de código, código inline nem links.

## Decisão

1. **Markdown restrito** em `explanation`, `task`, `concept` e no texto das dicas. São suportados:
   - parágrafos;
   - listas `-`/`*` e `1.`;
   - blocos de código cercados por ```` ``` ````, com o botão "copiar";
   - `código inline`, **negrito**, *itálico*;
   - links `[texto](https://…)`.
2. **Sem HTML.** O portal transforma o texto em uma árvore de dados e renderiza só elementos React (`apps/web/src/portal/markdown.ts` e `Markdown.tsx`). Não há `dangerouslySetInnerHTML`, e tags aparecem como texto.
   - Links só com `https://`, mesma regra no contrato e no portal. Abrem em nova aba com `rel="noopener noreferrer"` e sem referrer.
   - Link com URL fora da regra vira texto.
3. **Campos novos, opcionais e aditivos** ao `v1alpha1`:
   - `steps[].references[]` (`title`, `url` https, até 8);
   - `learning.wrapUp` (`text` em Markdown e `references`), exibido como "Para ir além" no resumo de conclusão.
   - Os campos não têm valor padrão serializado, então o digest de manifestos existentes não muda. O JSON Schema foi regenerado.
4. **Exposição.** O conteúdo da etapa (incluindo `references`) só aparece quando a etapa não está bloqueada, como antes. `wrapUp` é público dentro da sessão do aluno. Nada disso é carregado pela plataforma: são links para o aluno abrir.

## Consequências

- Labs podem mostrar o código antes e depois de uma correção e citar fontes como OWASP e CWE.
- O renderizador próprio evita uma dependência nova em produção. O `vitest` entra só como dependência de desenvolvimento para testar o parser. O CI ganha o job `web` (typecheck e testes).
- Imagens, tabelas e títulos não são suportados. Se forem necessários, a mudança será registrada aqui.

## Testes

- `packages/contracts/tests/test_manifest.py`:
  - campos aceitos;
  - URLs `javascript:`, `http:`, `data:`, relativas ao protocolo, com aspas e com espaço recusadas;
  - digest do LAB-000 inalterado.
- `apps/web/src/portal/markdown.test.ts`:
  - HTML vira texto;
  - links inseguros viram texto;
  - código preservado literalmente;
  - SQL com `*` e `--` não vira ênfase.
- `apps/backend/tests/test_integration_progress.py`: `references` e `wrapUp` expostos e omitidos em etapa bloqueada.
