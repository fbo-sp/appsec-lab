# Mesa de Crédito · Cooperativa Credimova (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de **SSRF** (Server-Side Request Forgery) para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> (busca no servidor) -> serviços internos simulados
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/importador_controller.py` — recebe a URL do formulário e chama o serviço.
- `services/importador_service.py` — **busca a URL no servidor**. É aqui que está a decisão de segurança.
- `controllers/auth_controller.py` + `services/auth_service.py` — login da equipe interna (não é o foco).
- `interno/servicos.py` — dois serviços internos **simulados** que sobem junto com a aplicação, só em
  loopback: o **Serviço de Documentos** (`127.0.0.1:8090`, destino legítimo) e o **Console de
  Infraestrutura** (`127.0.0.1:9000`, uso interno, guarda credenciais). Não mexa aqui: eles só existem
  para o importador ter o que buscar.

## A feature

Na **Mesa**, o analista cola a URL de um documento no sistema parceiro e a aplicação busca a prévia. A
busca é feita pelo **servidor** da aplicação — então, se nada for validado, o servidor pode ser levado a
buscar endereços internos que o analista jamais deveria alcançar.
