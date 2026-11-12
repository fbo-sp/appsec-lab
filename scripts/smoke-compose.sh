#!/usr/bin/env bash
# Smoke test do ambiente Docker Compose local: sobe a pilha, executa o ciclo da sessão e derruba.
# Uso: scripts/smoke-compose.sh [--no-build]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$ROOT/infrastructure/local/docker-compose.yml")
BUILD=(--build); [ "${1:-}" = "--no-build" ] && BUILD=(--no-build)
API=http://127.0.0.1:8000
trap '"${COMPOSE[@]}" logs --no-color api worker | tail -40; "${COMPOSE[@]}" down -v >/dev/null 2>&1 || true' EXIT
"${COMPOSE[@]}" up -d --wait "${BUILD[@]}"
json() { python3 -c "import json,sys; print(json.load(sys.stdin)$1)"; }
wait_status() {
  for _ in $(seq 1 40); do
    st=$(curl -sf -H "X-Dev-User: smoke" "$API/api/v1/sessions/$1" | json '["status"]')
    [ "$st" = "$2" ] && { echo "$st"; return 0; }; sleep 0.5
  done; echo "esperado $2, obtido $st" >&2; return 1
}
code=$(curl -s -o /dev/null -w "%{http_code}" -H "X-Dev-User: admin" -H "X-Dev-Roles: admin" \
  -H "Content-Type: application/yaml" --data-binary @"$ROOT/laboratories/LAB-000-hello-benign/manifest.yaml" \
  "$API/api/v1/admin/lab-releases")
[ "$code" = "201" ] || { echo "registro falhou: $code" >&2; exit 1; }
SID=$(curl -sf -H "X-Dev-User: smoke" -H "Idempotency-Key: smoke-key-0001" -H "Content-Type: application/json" \
  -d '{"labId":"LAB-000","version":"0.1.0","variantId":"python-http"}' "$API/api/v1/sessions" | json '["sessionId"]')
wait_status "$SID" READY
[ "$(curl -s -o /dev/null -w "%{http_code}" -H "X-Dev-User: intruso" "$API/api/v1/sessions/$SID")" = "404" ]
curl -sf -X DELETE -H "X-Dev-User: smoke" "$API/api/v1/sessions/$SID" >/dev/null
wait_status "$SID" TERMINATED
[ "$("${COMPOSE[@]}" exec -T api id -u)" = "10001" ]
echo "SMOKE OK"
