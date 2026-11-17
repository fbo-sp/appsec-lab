# Bem Cuidar Reembolso · Operadora Bem Cuidar (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **consumo inseguro de API** (OWASP API10) para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                                 |
                                 +-> services/parceiro_client.py -> API do Rede Atlas Credenciados
```

- `controllers/painel_controller.py` — o painel e o botão que consulta o parceiro.
- `services/parceiro_client.py` — a chamada HTTP à API do parceiro.
- `services/consulta_service.py` — **grava o que o parceiro respondeu.** É aqui que está a falha.
- `controllers/parceiro_simulado.py` — a SIMULAÇÃO do parceiro, com o interruptor de "modo comprometido"
  em `/parceiro/admin`. Não é parte da correção.

## A feature

Para cada pedido, o Bem Cuidar Reembolso consulta o Rede Atlas Credenciados e grava o valor de reembolso
que ele devolve. O contrato combinado diz que a resposta tem só `referencia` e `valor_reembolso`, com valor
entre 0 e R$ 20.000. O serviço grava o que vier: se o parceiro for comprometido, valores absurdos
entram no banco e um campo fora do contrato aprova a pedido sozinho. A defesa é tratar a
resposta do parceiro como entrada não confiável: conferir campos e faixas antes de usar.
