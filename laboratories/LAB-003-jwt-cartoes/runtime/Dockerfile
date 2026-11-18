# Imagem do LAB-003 (JWT, Node.js + Express) para o runtime Docker LOCAL (ADR-008).
# CONTÉM VULNERABILIDADE INTENCIONAL: usar só em rede interna da sessão, nunca exposta (ver ADR-008).
# Build: scripts/lab-local.sh (ou scripts/lab-local.ps1 no Windows), que antes constrói as bases.
FROM cecyber-labs/base-node:local

USER root
# Dependências fora do workspace: não entram no snapshot avaliado nem podem ser editadas pelo aluno.
# curl: usado pelo aluno no terminal para chamar a API.
COPY package.json package-lock.json /opt/lab/
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/* \
 && cd /opt/lab && npm ci --omit=dev --no-audit --no-fund && npm cache clean --force
ENV NODE_PATH=/opt/lab/node_modules
USER 10001

# Conteúdo inicial do workspace: copiado para o volume da sessão na primeira montagem.
COPY --chown=10001:10001 workspace/ /workspace/
EXPOSE 8080
# Pronto = aplicação (8080) e agente de workspace (7681) respondendo.
HEALTHCHECK --interval=3s --timeout=10s --start-period=3s --retries=20 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/', timeout=2); u.urlopen('http://127.0.0.1:7681/healthz', timeout=2)"]
# Reinicia ao salvar (node --watch). A saída do processo também vai para /tmp/app.log.
CMD ["sh", "-c", "node --watch app.js 2>&1 | tee -a /tmp/app.log"]
