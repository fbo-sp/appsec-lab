# Diretório de Profissionais · Clínica Lumen (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, uma falha de segurança na **busca de pessoas no diretório** para você encontrar e corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> diretorio.py (diretório simulado)
                 |
                 +-> templates/  (monta o HTML de resposta)
```

- `controllers/painel_controller.py` — recebe o nome digitado na busca e chama o serviço.
- `services/busca_service.py` — **a busca**. Monta um filtro no estilo LDAP a partir do nome e
  consulta o diretório. **É aqui que está a falha.**
- `diretorio.py` — o diretório corporativo SIMULADO e um avaliador mínimo de filtro `(cn=PADRÃO)`.
  Não há servidor LDAP real; é só o suficiente para mostrar a injeção.
- `controllers/auth_controller.py`, `services/auth_service.py` — o login (não é o foco).

## A feature

O funcionário entra e, no painel, digita o nome de um colega para achá-lo no diretório. A busca monta
o filtro `(cn=NOME)` e lista quem casa. O problema: o nome entra **cru** no filtro. Como o `*` é
curinga nos filtros LDAP, buscar por `*` vira `(cn=*)` e **lista o diretório inteiro** — é injeção de
LDAP. A defesa é **escapar os caracteres especiais** do filtro (`*`, `(`, `)`, `\`) antes de montá-lo,
para que o que o usuário digita seja tratado como texto, não como sintaxe de filtro.
