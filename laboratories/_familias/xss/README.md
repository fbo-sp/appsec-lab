# Família `xss` (A1): XSS refletido e armazenado

Gera LAB-005 (A1-FIN, Banco Aurora Digital), LAB-006 (A1-SAU, Rede Lumina Diagnósticos) e LAB-007
(A1-IND, Voltera Distribuidora de Energia). ADR-021 descreve o modelo de família.

## Código-base comum (`modelo/`)

Aplicação Flask em camadas (controllers, services, repositories, models) com dois perfis:

- **usuário comum**: busca e cadastra registros do domínio (`/[[rota]]?q=...`, `POST /[[rota]]/novo`);
- **equipe interna**: vê no `/painel` os registros de todos, com o campo livre ("observação").

Vulnerabilidades intencionais:

1. `templates/[[rota]].html` mostra o termo da busca com `{{ termo|safe }}` (XSS refletido);
2. `templates/painel.html` mostra a observação com `{{ item.nota|safe }}` (XSS armazenado);
3. `limpar_texto` no service só remove `<script>` (lista de bloqueio, que o aluno contorna);
4. a sessão de demonstração grava um cookie sem `HttpOnly` com um valor fictício, que o aluno lê com
   `this.outerHTML=document.cookie` (o preview roda num iframe sem `allow-modals`, então `alert()` não abre).

Correção esperada: tirar o `|safe` (ou trocar por `|e`) nos dois templates. A suíte
`xss/python-flask/output-encoding-<ramo>-v1` reprova correção só na busca e listas de bloqueio maiores
(`<svg onload>`, `<details ontoggle>`); os testes com Docker real estão em
`apps/backend/tests/test_xss_family_validation.py`.

## O que muda por ramo (`ramos.yaml`)

Empresa, história, nomes do domínio (entidade, rota, campos), usuários e senhas fictícios, valores dos
cookies e dados do seed. Os valores que a suíte usa (logins, cookies, termo legítimo) ficam também em
`XSS_RAMOS`, no registro protegido (`apps/backend/app/validation/suites_familias.py`); os dois têm de
bater.

## Gerar de novo

```bash
uv run python scripts/gerar-familia.py xss          # regrava LAB-005..007
uv run python scripts/gerar-familia.py --check --all  # o mesmo teste da CI
```

Não edite as pastas `LAB-00N-*` à mão. Uma mudança no modelo que altera o lab publicado exige versão
nova no manifesto (release imutável) e entrada em `docs/catalogo/historico-versoes.yaml`.
