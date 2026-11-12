#!/usr/bin/env bash
# Smoke test do ambiente Docker Compose local: sobe a pilha, executa o ciclo da sessão e derruba.
# Uso: scripts/smoke-compose.sh [--no-build] [--docker-runtime]
#   --docker-runtime: usa o runtime Docker LOCAL (ADR-008) e o LAB-000 como contêiner real.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$ROOT/infrastructure/local/docker-compose.yml")
BUILD=(--build); DOCKER_RT=0
for arg in "$@"; do
  case "$arg" in
    --no-build) BUILD=(--no-build);;
    --docker-runtime) DOCKER_RT=1;;
    *) echo "argumento desconhecido: $arg" >&2; exit 2;;
  esac
done
if [ "$DOCKER_RT" = 1 ]; then
  COMPOSE+=(-f "$ROOT/infrastructure/local/docker-compose.docker-runtime.yml")
  export DOCKER_SOCKET_GID="${DOCKER_SOCKET_GID:-$(stat -c %g /var/run/docker.sock)}"
fi
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
if [ "$DOCKER_RT" = 1 ]; then
  "$ROOT/scripts/lab-local.sh" "$API"
else
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "X-Dev-User: admin" -H "X-Dev-Roles: admin" \
    -H "Content-Type: application/yaml" --data-binary @"$ROOT/laboratories/LAB-000-hello-benign/manifest.yaml" \
    "$API/api/v1/admin/lab-releases")
  [ "$code" = "201" ] || { echo "registro falhou: $code" >&2; exit 1; }
fi
SID=$(curl -sf -H "X-Dev-User: smoke" -H "Idempotency-Key: smoke-key-0001" -H "Content-Type: application/json" \
  -d '{"labId":"LAB-000","version":"0.2.0","variantId":"python-http"}' "$API/api/v1/sessions" | json '["sessionId"]')
wait_status "$SID" READY
if [ "$DOCKER_RT" = 1 ]; then
  C="cecyber-lab-$SID"
  [ "$(docker inspect -f '{{.Config.User}} {{.HostConfig.ReadonlyRootfs}}' "$C")" = "10001 true" ]
  [ "$(docker network inspect -f '{{.Internal}}' "$C-net")" = "true" ]
  [ -z "$(docker port "$C")" ] || { echo "laboratório publicou portas no host" >&2; exit 1; }
  docker exec "$C" python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=3)"
  echo "contêiner do laboratório OK: $C"
  # Gateway: ticket de uso único -> cookie -> preview e API de arquivos via agente.
  JAR=$(mktemp)
  ticket_url() {
    curl -sf -H "X-Dev-User: smoke" -H "Content-Type: application/json" -d "{\"purpose\":\"$1\"}" \
      "$API/api/v1/sessions/$SID/gateway-ticket" | json '["url"]'
  }
  PV=$(ticket_url preview)
  [ "$(curl -s -o /dev/null -w "%{http_code}" -c "$JAR" "$PV")" = "303" ]
  [ "$(curl -s -o /dev/null -w "%{http_code}" "$PV")" = "401" ] || { echo "ticket reutilizável" >&2; exit 1; }
  for _ in $(seq 1 20); do curl -sf -b "$JAR" http://127.0.0.1:8002/ | grep -q "LAB-000" && break; sleep 0.5; done
  curl -sf -b "$JAR" http://127.0.0.1:8002/ | grep -q "LAB-000"
  WSU=$(ticket_url workspace)
  [ "$(curl -s -o /dev/null -w "%{http_code}" -c "$JAR" "$WSU")" = "303" ]
  curl -sf -b "$JAR" -H "X-Cecyber-Workspace: 1" \
    "http://127.0.0.1:8001/s/$SID/__cecyber/api/files?path=" | grep -q index.html
  [ "$(curl -s -o /dev/null -w "%{http_code}" -H "X-Dev-User: intruso" -H "Content-Type: application/json" \
    -d '{"purpose":"preview"}' "$API/api/v1/sessions/$SID/gateway-ticket")" = "404" ]
  echo "gateway OK: preview e arquivos acessíveis só com ticket do dono"
  # Validação (ADR-010): etapa de resposta na API; etapa http avaliada pelo worker numa cópia isolada.
  evaluate() {
    curl -sf -H "X-Dev-User: smoke" -H "Idempotency-Key: $3" -H "Content-Type: application/json" \
      -d "$2" "$API/api/v1/sessions/$SID/steps/$1/evaluations"
  }
  [ "$(evaluate explore '{"answer":"lab"}' smoke-eval-0001 | json '["status"]')" = "PASSED" ]
  EV=$(evaluate edit-page '{}' smoke-eval-0002 | json '["evaluationId"]')
  for _ in $(seq 1 90); do
    EVST=$(curl -sf -H "X-Dev-User: smoke" "$API/api/v1/sessions/$SID/evaluations/$EV" | json '["status"]')
    case "$EVST" in QUEUED|RUNNING) sleep 1;; *) break;; esac
  done
  # Workspace não editado: a verificação de conteúdo falha, a de disponibilidade passa (nunca ERROR).
  [ "$EVST" = "FAILED" ] || { echo "avaliação http terminou em $EVST" >&2; exit 1; }
  [ -z "$(docker ps -aq --filter label=io.cecyber.appsec-labs.evaluation-id)" ] \
    || { echo "recursos de avaliação não foram removidos" >&2; exit 1; }
  echo "validação OK: resposta aprovada; avaliação http executada fora do workspace e limpa"
fi
[ "$(curl -s -o /dev/null -w "%{http_code}" -H "X-Dev-User: intruso" "$API/api/v1/sessions/$SID")" = "404" ]
curl -sf -X DELETE -H "X-Dev-User: smoke" "$API/api/v1/sessions/$SID" >/dev/null
wait_status "$SID" TERMINATED
if [ "$DOCKER_RT" = 1 ]; then
  [ -z "$(docker ps -aq --filter label=io.cecyber.appsec-labs.session-id="$SID")" ] \
    || { echo "contêiner do laboratório não foi removido" >&2; exit 1; }
  ! docker network inspect "cecyber-lab-$SID-net" >/dev/null 2>&1 || { echo "rede não removida" >&2; exit 1; }
  ! docker volume inspect "cecyber-lab-$SID-ws" >/dev/null 2>&1 || { echo "volume não removido" >&2; exit 1; }
  [ "$(curl -s -o /dev/null -w "%{http_code}" -b "$JAR" http://127.0.0.1:8002/)" = "403" ] \
    || { echo "gateway não revogou o acesso após o término" >&2; exit 1; }
  rm -f "$JAR"
fi
[ "$("${COMPOSE[@]}" exec -T api id -u)" = "10001" ]
echo "SMOKE OK"
