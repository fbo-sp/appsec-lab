#!/usr/bin/env bash
# Constrói a imagem LOCAL do LAB-000 e registra a release apontando para o ID local da imagem.
# Uso: scripts/lab-local.sh [API]   (padrão http://127.0.0.1:8000). Somente runtime Docker local (ADR-008).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API="${1:-http://127.0.0.1:8000}"
LAB="$ROOT/laboratories/LAB-000-hello-benign"
# Base com o agente de workspace (arquivos + terminal). SKIP_BASE_BUILD=1 reaproveita uma base existente.
if [ "${SKIP_BASE_BUILD:-0}" != 1 ]; then
  docker build -q -t cecyber-labs/base-python:local "$ROOT/laboratories/_base/python" >/dev/null
fi
docker build -q -t cecyber-labs/lab-000-hello:local "$LAB/runtime" >/dev/null
ID=$(docker image inspect --format '{{.Id}}' cecyber-labs/lab-000-hello:local)
echo "imagem local: $ID"
MANIFEST=$(sed -E "s#^(    image: ).*@sha256:[0-9a-f]{64}#\1local/labs/lab-000-hello@${ID}#" "$LAB/manifest.yaml")
code=$(printf '%s' "$MANIFEST" | curl -s -o /dev/stderr -w "%{http_code}" -H "X-Dev-User: admin" \
  -H "X-Dev-Roles: admin" -H "Content-Type: application/yaml" --data-binary @- "$API/api/v1/admin/lab-releases")
echo
case "$code" in
  200|201) echo "LAB-000 registrado ($code)";;
  409) echo "A release LAB-000@0.1.0 já existe com outra imagem. Recrie o banco local:" >&2
       echo "  docker compose -f infrastructure/local/docker-compose.yml down -v" >&2; exit 1;;
  *) echo "registro falhou: HTTP $code" >&2; exit 1;;
esac
