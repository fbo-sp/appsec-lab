#!/usr/bin/env bash
# Executa lint, tipagem e testes (unitários + integração com PostgreSQL local descartável).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
uv sync --frozen 2>/dev/null || uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy packages/contracts/src apps/backend/app
if [ -z "${TEST_DATABASE_URL:-}" ]; then
  "$ROOT/scripts/dev-db.sh" start
  export TEST_DATABASE_URL="$("$ROOT/scripts/dev-db.sh" url appsec_labs_test)"
fi
uv run pytest "$@"
