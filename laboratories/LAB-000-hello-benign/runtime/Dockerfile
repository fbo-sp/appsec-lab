# Imagem do LAB-000 (BENIGNO) para o runtime Docker LOCAL (ADR-008). Sem vulnerabilidade intencional.
# Build: scripts/lab-local.sh build  (ou scripts/lab-local.ps1 no Windows)
FROM python:3.12-slim

# Timeout folgado: com 100 millicores a inicialização do Python leva alguns segundos.
# Usuário não-root obrigatório: o adapter recusa imagens sem USER numérico != 0.
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin lab \
 && mkdir -p /workspace && chown 10001:10001 /workspace
# Conteúdo inicial do workspace: copiado para o volume da sessão na primeira montagem.
COPY --chown=10001:10001 workspace/ /workspace/
USER 10001
WORKDIR /workspace
EXPOSE 8080
HEALTHCHECK --interval=3s --timeout=10s --start-period=2s --retries=10 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=1)"]
CMD ["python", "-m", "http.server", "8080", "--bind", "0.0.0.0"]
