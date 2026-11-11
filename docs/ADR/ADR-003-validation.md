# ADR-003: Runner e verificação protegida

- **Status:** Proposto, **decisão pendente**
- **Data:** 2026-11-11
- **Decisores:** Arquitetura, DevSecOps e Segurança (a confirmar)

## Contexto

Como executar verificadores confiáveis sobre conteúdo que o aluno pode manipular?

## Alternativa preliminar

Serviço/runner externo ao workspace, snapshot consistente e resultados autenticados.

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
