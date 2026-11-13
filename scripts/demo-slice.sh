#!/usr/bin/env bash
# Demonstração ponta a ponta da 1ª fatia com processos reais (API + worker) e FakeRuntimeAdapter.
# Pré-requisitos: uv, PostgreSQL local (scripts/dev-db.sh start). Nenhum contêiner é executado.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGDIR="${LOGDIR:-$(mktemp -d)}"; mkdir -p "$LOGDIR"
export APP_ENV=local AUTH_MODE=dev RUNTIME_ADAPTER=fake WORKER_POLL_SECONDS=0.2 RECONCILE_INTERVAL_SECONDS=1
export DATABASE_URL="${DATABASE_URL:-$("$ROOT/scripts/dev-db.sh" url)}"
API=http://127.0.0.1:8765
cd "$ROOT/apps/backend"
uv run alembic upgrade head
uv run uvicorn --factory app.main:app_factory --port 8765 >"$LOGDIR/api.log" 2>&1 &
API_PID=$!
uv run python -m app.workers.run >"$LOGDIR/worker.log" 2>&1 &
WK_PID=$!
trap 'kill $API_PID $WK_PID 2>/dev/null || true' EXIT
for _ in $(seq 1 50); do curl -sf "$API/healthz" >/dev/null && break; sleep 0.2; done

ADMIN=(-H "X-Dev-User: admin-demo" -H "X-Dev-Roles: admin")
ALUNO=(-H "X-Dev-User: aluno-demo" -H "X-Dev-Roles: student")
echo "== 1. Registrar LAB-000 (benigno)"
curl -s "${ADMIN[@]}" -H "Content-Type: application/yaml" --data-binary @"$ROOT/laboratories/LAB-000-hello-benign/manifest.yaml" \
  -w " [HTTP %{http_code}]\n" "$API/api/v1/admin/lab-releases" | cut -c1-200
echo "== 2. Criar sessão (Idempotency-Key)"
KEY="demo-$(date +%s%N)"
SID=$(curl -s "${ALUNO[@]}" -H "Idempotency-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"labId":"LAB-000","version":"0.2.1","variantId":"python-http"}' "$API/api/v1/sessions" | python3 -c 'import json,sys; print(json.load(sys.stdin)["sessionId"])')
echo "sessionId=$SID"
echo "== 3. Repetir com a mesma chave (deve retornar a mesma sessão)"
curl -s "${ALUNO[@]}" -H "Idempotency-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"labId":"LAB-000","version":"0.2.1","variantId":"python-http"}' "$API/api/v1/sessions" | python3 -c 'import json,sys; print(json.load(sys.stdin)["sessionId"])'
echo "== 4. Aguardar READY"
for _ in $(seq 1 50); do
  ST=$(curl -s "${ALUNO[@]}" "$API/api/v1/sessions/$SID" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])')
  [ "$ST" = "READY" ] && break; sleep 0.2
done; echo "status=$ST"
echo "== 5. Outro aluno não enxerga a sessão"
curl -s -o /dev/null -w "HTTP %{http_code}\n" -H "X-Dev-User: outro-aluno" "$API/api/v1/sessions/$SID"
echo "== 6. Encerrar"
curl -s -X DELETE "${ALUNO[@]}" -w " [HTTP %{http_code}]\n" "$API/api/v1/sessions/$SID" | cut -c1-120
for _ in $(seq 1 50); do
  ST=$(curl -s "${ALUNO[@]}" "$API/api/v1/sessions/$SID" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])')
  [ "$ST" = "TERMINATED" ] && break; sleep 0.2
done; echo "status=$ST"
echo "== Logs estruturados do worker (amostra) em $LOGDIR"
grep '"session_id"\|"resource_id"' "$LOGDIR/worker.log" | grep "$SID" | head -5
