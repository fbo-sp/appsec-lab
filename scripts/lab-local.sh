#!/usr/bin/env bash
# Constrói as imagens LOCAIS dos laboratórios e registra cada release apontando para o ID local da imagem.
# Uso: scripts/lab-local.sh [API]   (padrão http://127.0.0.1:8000). Somente runtime Docker local (ADR-008).
# LAB-001 a LAB-004 contêm vulnerabilidades INTENCIONAIS: rodam só na rede interna da sessão, nunca expostos.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API="${1:-http://127.0.0.1:8000}"
LABS=(LAB-000-hello-benign LAB-001-sqli-clinica LAB-002-idor-banco LAB-003-jwt-cartoes LAB-004-cmdi-industria)
# Base com o agente de workspace (arquivos + terminal). SKIP_BASE_BUILD=1 reaproveita uma base existente.
if [ "${SKIP_BASE_BUILD:-0}" != 1 ]; then
  docker build -q -t cecyber-labs/base-python:local "$ROOT/laboratories/_base/python" >/dev/null
  # Base Node.js (LAB-003): parte da base Python, que traz o agente de workspace.
  docker build -q -t cecyber-labs/base-node:local "$ROOT/laboratories/_base/node" >/dev/null
fi
for dir in "${LABS[@]}"; do
  LAB="$ROOT/laboratories/$dir"
  NAME=$(sed -nE 's#^    image: registry\.local/labs/([a-z0-9-]+)@sha256:.*#\1#p' "$LAB/manifest.yaml")
  ID_LAB=$(sed -nE 's#^  id: (LAB-[0-9]{3})$#\1#p' "$LAB/manifest.yaml")
  VERSION=$(sed -nE 's#^  version: ([0-9][^ ]*)$#\1#p' "$LAB/manifest.yaml" | head -1)
  # Cada release registrada fica presa a uma imagem com tag de versão (cecyber-labs/<nome>:<versão>).
  # Release é imutável: se essa tag já existe, ela é reaproveitada e NADA é reconstruído para essa versão.
  # Sem isso, reconstruir a base trocava o ID das imagens e as releases já registradas ficavam órfãs.
  PINNED="cecyber-labs/$NAME:$VERSION"
  if docker image inspect "$PINNED" >/dev/null 2>&1; then
    echo "$ID_LAB@$VERSION: reaproveitando a imagem $PINNED"
  else
    # SKIP_LAB_BUILD=1 usa imagens já construídas (ex.: ambientes com proxy que exigem build próprio).
    if [ "${SKIP_LAB_BUILD:-0}" != 1 ]; then
      docker build -q -t "cecyber-labs/$NAME:local" "$LAB/runtime" >/dev/null
    fi
    docker tag "cecyber-labs/$NAME:local" "$PINNED"
  fi
  ID=$(docker image inspect --format '{{.Id}}' "$PINNED")
  echo "$ID_LAB: imagem local $ID"
  MANIFEST=$(sed -E "s#^(    image: ).*@sha256:[0-9a-f]{64}#\1local/labs/$NAME@${ID}#" "$LAB/manifest.yaml")
  code=$(printf '%s' "$MANIFEST" | curl -s -o /dev/stderr -w "%{http_code}" -H "X-Dev-User: admin" \
    -H "X-Dev-Roles: admin" -H "Content-Type: application/yaml" --data-binary @- "$API/api/v1/admin/lab-releases")
  echo
  case "$code" in
    200|201) echo "$ID_LAB registrado ($code)";;
    # Release imutável já publicada com outro conteúdo/imagem: avisa e segue para o próximo laboratório.
    409) echo "AVISO: $ID_LAB@$VERSION já está publicada com outra imagem ou conteúdo (409); mantida a versão existente." >&2
         echo "  Se as sessões desse lab falharem com 'imagem não encontrada', a imagem registrada foi removida:" >&2
         echo "  suba a versão no manifesto ou recrie o banco local (apaga os dados)." >&2;;
    *) echo "registro de $ID_LAB falhou: HTTP $code" >&2; exit 1;;
  esac
done
