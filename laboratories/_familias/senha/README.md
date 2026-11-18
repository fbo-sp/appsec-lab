# Família `senha` (A4): armazenamento inseguro de senha

Gera LAB-017 (A4-FIN, Cooperativa Credimova), LAB-018 (A4-SAU, Laboratórios Helios) e LAB-019
(A4-IND, Siderúrgica Pindorama). ADR-021 descreve o modelo de família.

## Código-base comum (`modelo/`)

Aplicação Flask em camadas (controllers, services, repositories, models) com um login e uma área logada
(`/painel`). As contas foram "importadas" de um sistema legado por ramo, e a senha de cada uma é guardada
pelo mesmo resumo que o legado usava.

Vulnerabilidade intencional:

- `services/auth_service.py` resume a senha com `hashlib.md5` (rápido e **sem sal**) e compara com o
  `senha_hash` do banco. O seed grava as senhas com esse mesmo MD5, simulando a importação do legado.

Dois reforços didáticos no seed de cada ramo:

- duas contas (`[[conta_c]]`/`[[conta_d]]`) usam a **mesma** senha, então têm o **mesmo** hash — mostra que
  MD5 sem sal é determinístico (etapa "sem-sal");
- a conta `teste.legado` usa a senha padrão do legado `Trocar@123`, para o aluno confirmar o MD5 puro
  (etapa "reversivel").

Correção esperada: adotar `werkzeug.security` (`generate_password_hash`/`check_password_hash`, scrypt com
sal e custo) e **migrar no login** — conferir o hash legado uma última vez e regravar no formato forte. O
`/painel` mostra se a senha do usuário logado já está no formato reforçado, então a migração fica visível.

A suíte `senha/python-flask/password-hashing-<ramo>-v1` faz login (migrando as contas), confere que o
login legítimo continua funcionando e **inspeciona o banco da cópia** (ADR-023): os hashes das contas que
entraram devem ser do werkzeug (`scrypt:`/`pbkdf2:`), nunca MD5 (32 hex), e precisam conferir com a senha
conhecida. Os testes com Docker real estão em `apps/backend/tests/test_senha_family_validation.py`.

## O que muda por ramo (`ramos.yaml`)

Empresa, história, nome do sistema legado, usuários e senhas fictícias. Os valores que a suíte usa
(logins, senhas, hashes esperados) ficam também em `SENHA_RAMOS`, no registro protegido
(`apps/backend/app/validation/suites_familias.py`); os dois têm de bater.

## Gerar de novo

```bash
uv run python scripts/gerar-familia.py senha        # regrava LAB-017..019
uv run python scripts/gerar-familia.py --check --all  # o mesmo teste da CI
```

Não edite as pastas `LAB-01N-*` à mão. Uma mudança no modelo que altera o lab publicado exige versão
nova no manifesto (release imutável) e entrada em `docs/catalogo/historico-versoes.yaml`.
