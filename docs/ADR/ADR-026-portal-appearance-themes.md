# ADR-026: Aparência do portal escolhida pelo usuário (Automático, Claro, Código escuro, Tudo escuro)

- **Status:** Aceito pelo PO quanto à visualização (2026-11-17, "a visualização tem apenas 3 modos e está aprovada"); modo Automático como padrão escolhido pelo PO no mesmo dia.
- **Data:** 2026-11-17
- **Relacionados:** ADR-009 (gateway e origens), ADR-022 (isolamento do preview), ADR-025 (perfil mobile)

## Contexto

Usuários em teste pediram o editor de código com fundo escuro, como nas IDEs. Até aqui o portal e o workspace seguiam o tema do sistema operacional (`prefers-color-scheme`), sem escolha do usuário; no escuro, o editor CodeMirror mantinha as cores de sintaxe do tema claro.

## Decisão

1. Quatro modos, escolhidos no botão **Aparência** do cabeçalho: **Automático** (padrão; segue o tema do sistema operacional, resolvendo para Claro ou Tudo escuro e acompanhando a troca do sistema), **Claro** (portal e editor claros), **Código escuro** (portal claro; lista de arquivos, editor e terminal escuros) e **Tudo escuro** (portal inteiro escuro). Quem escolhe um modo fixo deixa de seguir o sistema.
2. A escolha é salva **no perfil do usuário** (`users.ui_theme`, `GET/PUT /api/v1/me/preferences`), para valer em qualquer máquina do ambiente on-premises. O navegador guarda uma cópia para abrir a página já com as cores certas.
3. O portal aplica o modo com `data-tema` no documento, que troca os tokens de cor; o layout não muda. O workspace roda em outra origem e recebe o modo já resolvido (nunca "auto") por `postMessage` (`cecyber:tema`), aceito só do próprio pai e com formato exato, como a mensagem de visão existente.
4. No escuro, o editor usa um tema próprio (fundo e cores de sintaxe pensados para fundo escuro), não a inversão do tema claro.
5. As aplicações dos laboratórios **não mudam**: rodam no preview, em outra origem (ADR-022), com as próprias cores, inclusive na moldura de celular dos labs mobile (ADR-025).

## Consequências

- Backend: coluna `users.ui_theme` (migração 0006) e rotas de preferência do próprio usuário; valores fora da lista são recusados.
- Web: `portal/theme.ts`, `portal/Aparencia.tsx`, tokens escuros sob `:root[data-tema="escuro"]` em `styles.css` e `workspace.css`, `workspace/editorTheme.ts`.
- Quem não escolhe nada mantém o comportamento anterior (segue o sistema), agora com o editor usando o tema escuro próprio quando o sistema está escuro.
