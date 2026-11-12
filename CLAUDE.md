# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Orientações gerais

Use `AGENTS.md` como instrução principal do projeto: leia-o integralmente antes de alterar código, documentação ou infraestrutura. A fonte de verdade de produto é `docs/00_PRODUCT_VISION.md` e `docs/02_PRD.md`. Responda e documente em português do Brasil; identificadores técnicos em inglês.

Antes de executar um trabalho, informe quais FR/NFR, histórias, ADRs e testes serão afetados. Não faça suposições silenciosas sobre isolamento, acesso à rede, permissões ou avaliação. Registre decisões em `docs/ADR/` (`Proposto` ≠ `Aprovado`). Mantenha implementação e documentação sincronizadas.

No início de cada sessão, leia `docs/25_DEVELOPMENT_STATUS.md` (estado verificável, pendências, bloqueadores e próxima tarefa), `docs/24_IMPLEMENTATION_BACKLOG.md` (itens `IMP-*`) e `docs/22_PROJECT_INITIAL_ASSESSMENT.md` (lacunas `G-*`). Ao concluir um incremento, atualize o `docs/25` com o comando executado e o resultado; não declare tarefa concluída sem essa evidência.

## Atualização v0.3

Nome oficial CECyber AppSec Labs; on-premises é premissa de implantação. Antes de alterar o fluxo de laboratórios, ler `docs/21_LEARNING_EXPERIENCE_SPEC.md` e `docs/11_LAB_MANIFEST_SPEC.md`. Progressão e hints são geridos por API com verificação backend.

## Comandos

Workspace Python 3.12+ gerenciado por `uv` (raiz `pyproject.toml`, membros `packages/contracts` e `apps/backend`; configuração de ruff, mypy e pytest fica na raiz).

```bash
scripts/test.sh                       # uv sync + ruff check + ruff format --check + mypy strict + pytest
scripts/test.sh -k idempot            # argumentos extras vão para o pytest
uv run pytest apps/backend/tests/test_unit_state_machine.py::nome_do_teste   # teste isolado
uv run mypy packages/contracts/src apps/backend/app
uv run python -m cecyber_contracts validate laboratories/LAB-000-hello-benign/manifest.yaml
uv run python -m cecyber_contracts export-schema packages/contracts/schemas/appseclab.v1alpha1.schema.json
```

- Testes de integração (`test_integration_*`, que usam a fixture `engine`) exigem `TEST_DATABASE_URL`; sem ela são **pulados**, não falham. `scripts/test.sh` sobe automaticamente um PostgreSQL descartável sem Docker (`scripts/dev-db.sh start`, porta 54329, loopback, `trust`). Para rodar pytest direto: `export TEST_DATABASE_URL=$(scripts/dev-db.sh url appsec_labs_test)`.
- A fixture `engine` faz `DROP SCHEMA public CASCADE` e aplica as migrações: nunca aponte `TEST_DATABASE_URL` para um banco com dados.
- Migrações (em `apps/backend`): `uv run alembic upgrade head` / `downgrade base`. Ao mudar `app/db/models.py`, crie nova revisão em `migrations/versions/` e mantenha `TABLES` em `apps/backend/tests/conftest.py` atualizada.
- Executar localmente (em `apps/backend`, com `DATABASE_URL=$(../../scripts/dev-db.sh url) APP_ENV=local AUTH_MODE=dev`): `uv run uvicorn --factory app.main:app_factory --port 8000` (Swagger em `/api/docs`) e `uv run python -m app.workers.run`.
- Demonstração ponta a ponta: `scripts/demo-slice.sh` (sem Docker) ou `scripts/smoke-compose.sh` / `infrastructure/local/docker-compose.yml` (Docker; no Windows, `scripts/demo-local.ps1`).
- Autenticação de desenvolvimento: cabeçalhos `X-Dev-User: <id>` e `X-Dev-Roles: student|instructor|admin`.
- O CI (`.github/workflows/ci.yml`) roda os mesmos passos de `scripts/test.sh`, valida o manifesto do LAB-000 e executa o smoke do Compose.

## Arquitetura

Estado atual: primeira fatia do **plano de controle** com runtime **simulado**. Não há sandbox real, OIDC, workspace, gateway, validador nem laboratórios vulneráveis; `apps/frontend`, `services/gateway` e `services/validator` são apenas READMEs.

- **`packages/contracts`** (`cecyber_contracts`): modelo Pydantic do manifesto `AppSecLab v1alpha1` (ADR-006), validação estrutural e semântica, digest canônico e o JSON Schema exportado em `schemas/`. O schema é gerado a partir do modelo: regenere-o com `export-schema` ao mudar `manifest.py`. Manifestos de laboratórios ficam em `laboratories/<LAB-ID>/manifest.yaml`.
- **`apps/backend`** (`app`): monólito modular FastAPI + workers, SQLAlchemy **síncrono** + psycopg. A tabela de módulos está em `apps/backend/README.md`. Pontos que exigem ler vários arquivos:
  - **Fluxo de sessão:** `POST /api/v1/sessions` (com `Idempotency-Key`) grava a sessão em `REQUESTED` e enfileira um job `PROVISION` na mesma transação. O worker (`workers/provisioner.py`) faz o claim com `FOR UPDATE SKIP LOCKED` + lease (`jobs/queue.py`, ADR-007), persiste o estado antes do efeito e chama o `RuntimePort`. `DELETE` enfileira `TERMINATE`; `TERMINATED` só após o adapter confirmar ausência. O reconciliador (`workers/reconciler.py`) trata TTL → `EXPIRED`, órfãos e jobs de término esgotados.
  - **Máquina de estados** explícita em `sessions/state_machine.py` (tabela `TRANSITIONS`); transições inválidas geram `409`. `VALIDATING` não é estado persistido. Toda mudança de estado passa por ela, com optimistic locking.
  - **Runtime:** só `app/runtime` conhece adapters concretos; o resto depende de `RuntimePort` (`runtime/port.py`, que documenta a semântica obrigatória de idempotência). Hoje existe apenas `FakeRuntimeAdapter`, e `tests/test_contract_runtime_port.py` é a suíte de contrato que todo adapter futuro deve passar.
  - **Configuração fail-closed** (`config.py`, `Settings.check`): `AUTH_MODE=dev` e o adapter `fake` só iniciam com `APP_ENV=local|test`; `oidc` e outros adapters recusam o início. Não afrouxe essas checagens.
  - **Auditoria** (`audit/service.py`) é gravada na mesma transação da operação. Erros seguem o envelope de `docs/13 §5` (`shared/errors.py`); logs são JSON com correlação por `X-Request-Id` e redaction.
  - **Ownership:** não-donos recebem `404` (não `403`); acesso de admin é auditado.
- Os testes usam `FakeClock` e chamam `run_once` do worker diretamente (ver `apps/backend/tests/conftest.py`) em vez de processos em segundo plano.
