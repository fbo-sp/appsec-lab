# Imagem do LAB-002 (IDOR, Flask + SQLite) para o runtime Docker LOCAL (ADR-008).
# CONTÉM VULNERABILIDADE INTENCIONAL: usar só em rede interna da sessão, nunca exposta (ver ADR-008).
# Build: scripts/lab-local.sh (ou scripts/lab-local.ps1 no Windows), que antes constrói a base.
FROM cecyber-labs/base-python:local

USER root
# curl: usado pelo aluno no terminal para chamar a API (etapa 4).
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir "flask==3.1.2"
USER 10001

# Conteúdo inicial do workspace: copiado para o volume da sessão na primeira montagem.
COPY --chown=10001:10001 workspace/ /workspace/
EXPOSE 8080
# Pronto = aplicação (8080) e agente de workspace (7681) respondendo.
HEALTHCHECK --interval=3s --timeout=10s --start-period=3s --retries=20 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/login', timeout=2); u.urlopen('http://127.0.0.1:7681/healthz', timeout=2)"]
# Recarrega ao salvar; o depurador interativo do Werkzeug fica DESLIGADO (é um console de execução).
# A saída do processo (inclusive erros de importação após salvar) também vai para /tmp/app.log.
CMD ["sh", "-c", "python -u -m flask --app app run --host 0.0.0.0 --port 8080 --reload --no-debugger 2>&1 | tee -a /tmp/app.log"]
