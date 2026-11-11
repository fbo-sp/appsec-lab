# ADR-007: Fila de jobs e outbox no PostgreSQL no MVP

- **Status:** Proposto, **implementado na 1ª fatia** (reversível)
- **Data:** 2026-11-11
- **Contexto de origem:** `06 §3` (Redis sugerido sem ADR); `22` G-11

## Contexto

O motor precisa de comandos assíncronos (provisionar, encerrar, futuramente avaliar) gravados **na mesma transação** que a mudança de estado (outbox), com retomada após falha de worker. A hospedagem é on-premises e cada componente adicional exige operação própria.

## Alternativas

| Alternativa | Prós | Contras |
|---|---|---|
| **A. PostgreSQL (`jobs` + `FOR UPDATE SKIP LOCKED` + lease)** | Transacional com o estado; nenhum componente novo; simples de testar | Throughput limitado (suficiente para dezenas de sessões); polling |
| B. Redis (fila/streams) + outbox no PostgreSQL | Baixa latência; padrão conhecido | Novo componente on-prem; exige dispatcher outbox→Redis; dupla fonte de estado |
| C. Broker (RabbitMQ/NATS) | Roteamento rico | Maior custo operacional; prematuro |

## Decisão proposta

Alternativa **A** no MVP. Índice único parcial impede dois jobs pendentes do mesmo tipo por sessão; lease vencido é recapturado; falhas com backoff exponencial limitado; job esgotado (`dead`) não finge sucesso e é re-enfileirado pelo reconciliador. Revisitar após o teste de carga de 30 sessões (IMP-603) ou se a avaliação exigir maior vazão.

## Consequências

+ Sem dependência operacional nova; operações idempotentes e auditáveis.
- Eventos de domínio para consumidores externos (`13 §6`) ainda não têm dispatcher; tabela `outbox_events` fica para IMP-207/F4.
