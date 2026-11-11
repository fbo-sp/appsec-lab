# CECyber AppSec Labs

Repositório de especificação **inicial** para desenvolvimento assistido por Codex e Claude Code de uma plataforma própria de laboratórios práticos de segurança de aplicações.

> **Estado:** planejamento, versão documental 0.3. Este repositório não contém uma implementação executável. As escolhas técnicas são propostas e precisam passar por PoCs e ADRs. Não declarar requisitos ou funcionalidades como implementados sem evidência.

## Onde começar

1. [`docs/00_PRODUCT_VISION.md`](docs/00_PRODUCT_VISION.md): visão, objetivos, limites e sucesso.
2. [`docs/02_PRD.md`](docs/02_PRD.md): requisitos do produto, fluxos, regras, aceite e prioridades.
3. [`docs/01_PROJECT_CHARTER.md`](docs/01_PROJECT_CHARTER.md): governança e marcos a confirmar.
4. [`docs/06_SYSTEM_ARCHITECTURE.md`](docs/06_SYSTEM_ARCHITECTURE.md): decisões técnicas iniciais e questões abertas.
5. [`docs/15_PRODUCT_BACKLOG.md`](docs/15_PRODUCT_BACKLOG.md): épicos e histórias sementes para refinamento.

## Convenções

- Documentos em português do Brasil, identificadores técnicos em inglês.
- Prioridade **P0**: indispensável ao piloto; **P1**: importante, negociável; **P2**: pós-MVP.
- `Proposto` não significa `Aprovado`; manter registro em ADRs.
- Contratos, testes de segurança e limites operacionais são obrigatórios antes de publicar ambientes vulneráveis.
- O MVP inclui **quatro laboratórios**: SQL Injection, IDOR, JWT e OS Command Injection.

## Fluxo com agentes de programação

Leia [`AGENTS.md`](AGENTS.md) (Codex) ou [`CLAUDE.md`](CLAUDE.md) (Claude Code); ambos direcionam à mesma fonte de verdade. Trabalhe em mudanças pequenas, com testes e atualizações de documentação. Não implemente componentes críticos sem requisitos de aceite ou ameaça documentados.

## Inventário

Consulte [`docs/INDEX.md`](docs/INDEX.md) para status de elaboração e ordem sugerida.

## Atualizações v0.3

- Nome oficial: **CECyber AppSec Labs**.
- Hospedagem inicial: **on-premises** (`docs/ADR/ADR-004-on-premises-hosting.md`).
- UX pedagógica obrigatória: `docs/21_LEARNING_EXPERIENCE_SPEC.md`.
- Especificações de manifesto, dados, API e escopo detalhadas em `docs/11` a `docs/14`.
- Requisitos pedagógicos acrescentados ao PRD e backlog US-031 a US-039.
- Pacote contém **apenas documentos Markdown**, ainda não código-fonte de aplicação ou migrações executáveis.
