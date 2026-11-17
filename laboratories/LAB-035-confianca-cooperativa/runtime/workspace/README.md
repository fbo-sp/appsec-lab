# Clube de Pontos · Cooperativa Credimova (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **confiança em dado do cliente** para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — a loja de pontos e o resgate de produtos.
- `services/loja_service.py` — **o resgate**. Debita os pontos do usuário pelo produto escolhido.
  É aqui que se decide de onde vem o custo. É aqui que está a falha.
- `repositories/produto_repository.py`, `models/produto.py` — os produtos e o custo real (no banco).
- `repositories/conta_repository.py`, `models/conta.py`, `database/seed.py` — a conta e o saldo de pontos.
- `services/auth_service.py` — login (não é o foco; as senhas já usam hash forte).

## A feature

O usuário vê o catálogo e resgata um produto gastando pontos. O custo de cada produto é um dado da
**loja**: ele está no banco, no servidor. O problema é que o formulário envia o custo junto com o
pedido, e o serviço **confia nesse custo** em vez de olhar o custo real do produto. Assim, quem ataca
manda o pedido com `custo=1` e leva um produto caro quase de graça. A defesa é o servidor **ignorar**
o custo do formulário e usar o custo do produto que está no banco.
