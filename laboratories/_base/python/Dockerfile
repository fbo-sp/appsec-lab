# Imagem base de laboratórios Python para o runtime LOCAL (ADR-008/ADR-009).
# Inclui o agente de workspace (arquivos + terminal) em /opt/agent, isolado do Python do aluno.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
RUN python -m venv /opt/agent \
 && /opt/agent/bin/pip install --no-cache-dir "aiohttp==3.12.15" \
 && useradd --uid 10001 --no-create-home --home-dir /tmp --shell /bin/bash lab \
 && mkdir -p /workspace && chown 10001:10001 /workspace
COPY agent.py /opt/agent/agent.py
COPY --chmod=0755 entrypoint.sh /opt/agent/entrypoint.sh
USER 10001
WORKDIR /workspace
ENTRYPOINT ["/opt/agent/entrypoint.sh"]
