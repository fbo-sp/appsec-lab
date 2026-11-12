# Imagem base de laboratórios Python para o runtime LOCAL (ADR-008/ADR-009).
# Inclui o agente de workspace (arquivos + terminal) em /opt/agent, isolado do Python do aluno.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
RUN python -m venv /opt/agent \
 && /opt/agent/bin/pip install --no-cache-dir "aiohttp==3.12.15" \
 && useradd --uid 10001 --no-create-home --home-dir /tmp --shell /bin/bash lab \
 && mkdir -p /workspace && chown 10001:10001 /workspace
COPY agent.py entrypoint.sh /opt/agent/
# chmod explícito: checkouts no Windows não preservam o bit de execução (e sem exigir BuildKit).
RUN chmod 0755 /opt/agent/entrypoint.sh && chmod 0644 /opt/agent/agent.py
USER 10001
WORKDIR /workspace
ENTRYPOINT ["/opt/agent/entrypoint.sh"]
