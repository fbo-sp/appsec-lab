# Imagem base de laboratórios Node.js para o runtime LOCAL (ADR-008/ADR-009).
# Parte da base Python, que já traz o agente de workspace (arquivos + terminal) em /opt/agent e o
# usuário sem privilégios 10001, e acrescenta o runtime Node.js 22 (LTS) copiado da imagem oficial.
# Build: scripts/lab-local.sh (ou .ps1), depois da base Python.
FROM node:22-slim AS node

FROM cecyber-labs/base-python:local
USER root
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
 && node --version && npm --version
ENV NODE_ENV=development NPM_CONFIG_UPDATE_NOTIFIER=false
USER 10001
