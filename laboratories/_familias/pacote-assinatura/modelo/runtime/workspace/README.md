# [[app_nome]] · [[empresa]] (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **integridade de dados** (OWASP A08) para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — a tela de [[pacote_tipo]] e o envio do pacote (`POST /pacotes`).
- `services/pacote_service.py` — **a importação do pacote.** Aplica os parâmetros sem conferir a
  assinatura do fornecedor. É aqui que está a falha.
- `repositories/parametro_repository.py` — grava os parâmetros em vigor.
- `pacotes_recebidos/` — o pacote mais recente enviado pelo [[fornecedor]].
- `config.py` — a chave HMAC FICTÍCIA combinada com o fornecedor.

## A feature

O [[fornecedor]] envia os [[pacote_tipo]] num arquivo JSON assinado com HMAC-SHA256. O arquivo passa
por um servidor de troca de arquivos antes de chegar aqui. A assinatura existe para provar que o
conteúdo veio do fornecedor e não mudou no caminho, mas só protege se alguém conferir.
