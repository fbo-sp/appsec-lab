# Imagem do LAB-000 (BENIGNO) para o runtime Docker LOCAL (ADR-008). Sem vulnerabilidade intencional.
# Build: scripts/lab-local.sh (ou scripts/lab-local.ps1 no Windows), que antes constrói a base.
FROM cecyber-labs/base-python:local

# Conteúdo inicial do workspace: copiado para o volume da sessão na primeira montagem.
COPY --chown=10001:10001 workspace/ /workspace/
EXPOSE 8080
# Timeout folgado: com 100 millicores a inicialização do Python leva alguns segundos.
# Pronto = aplicação (8080) e agente de workspace (7681) respondendo.
HEALTHCHECK --interval=3s --timeout=10s --start-period=2s --retries=10 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/', timeout=2); u.urlopen('http://127.0.0.1:7681/healthz', timeout=2)"]
CMD ["python", "-m", "http.server", "8080", "--bind", "0.0.0.0"]
