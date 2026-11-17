# Painel de Relatórios · Metalúrgica Delta (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **erros verbosos** (vazamento de informação em mensagens de erro) para você
encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — a área logada e a API `/api/relatorio`, que gera o relatório de
  um mês e, em caso de erro, responde pela ErroService.
- `services/erro_service.py` — **o tratamento de erro**. Monta a resposta de erro para o cliente.
  É aqui que está a falha.
- `services/relatorio_service.py` — gera o relatório (fonte de um erro quando o mês é inválido).
- `services/auth_service.py` — login (não é o foco; as senhas já usam hash forte).

## A feature

A API `/api/relatorio?mes=...` gera o relatório do mês. Quando o mês é inválido, o processamento
falha. O problema é o que a API faz com essa falha: ela devolve ao cliente a **mensagem interna da
exceção e o traceback completo** — caminhos de arquivos, nomes de módulos e pistas da tecnologia. Isso
ajuda quem ataca a mapear o sistema. A defesa é **registrar** o detalhe no log do servidor e devolver
ao cliente apenas uma **mensagem genérica**.
