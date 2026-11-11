# ADR-002: Isolamento dos laboratórios

- **Status:** Proposto, **decisão pendente**
- **Data:** 2026-11-11
- **Decisores:** Arquitetura, DevSecOps e Segurança (a confirmar)

## Contexto

Qual tecnologia e fronteira de isolamento suportam código de aluno deliberadamente adversarial?

## Alternativa preliminar

Avaliar gVisor, Kata e microVMs, regras de rede bloqueada e controles de privilégio; aprovar por teste.

## Critérios de avaliação

- Isolamento e superfície de ataque.
- Desempenho de inicialização e custo por sessão.
- Facilidade de operação, atualização e diagnóstico.
- Portabilidade e compatibilidade com os quatro laboratórios.
- Evidência de testes de segurança e resiliência.

## Consequências e riscos

**Pendentes de PoC.** Não tratar a alternativa como uma decisão concluída.

## Evidências requeridas

- [ ] PoC documentada.
- [ ] Comparação de alternativas.
- [ ] Threat model e controles mínimos aprovados.
- [ ] Parecer formal e data de aceite.
