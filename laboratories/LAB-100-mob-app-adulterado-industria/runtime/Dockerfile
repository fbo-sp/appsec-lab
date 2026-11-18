# Imagem do LAB-100 (L11-IND: app mobile simulado, Flask + SQLite) para o runtime Docker LOCAL (ADR-008).
# CONTÉM VULNERABILIDADE INTENCIONAL: usar só em rede interna da sessão, nunca exposta (ver ADR-008).
# Gerado por scripts/gerar-familia.py a partir de laboratories/_familias/mob-app-adulterado (ADR-021, ADR-025).
FROM cecyber-labs/base-python:local

USER root
RUN pip install --no-cache-dir "flask==3.1.2"
USER 10001

# Conteúdo inicial do workspace: copiado para o volume da sessão na primeira montagem.
COPY --chown=10001:10001 workspace/ /workspace/

# Serviço de integridade SIMULADO (a "loja", ver services/atestacao_service.py): o hash do pacote
# oficial (código do app como publicado) e a chave do selo ficam FORA do workspace, só para leitura.
USER root
RUN mkdir -p /opt/loja \
 && python -c "import hashlib; h = hashlib.sha256(); [h.update(open('/workspace/' + f, 'rb').read()) for f in ('static/app.js', 'static/regras.js')]; print(h.hexdigest())" > /opt/loja/pacote_oficial.sha256 \
 && python -c "import secrets; print(secrets.token_hex(32))" > /opt/loja/chave \
 && chmod 755 /opt/loja && chmod 444 /opt/loja/*
USER 10001
EXPOSE 8080
# Pronto = aplicação (8080) e agente de workspace (7681) respondendo.
HEALTHCHECK --interval=3s --timeout=10s --start-period=3s --retries=20 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/', timeout=2); u.urlopen('http://127.0.0.1:7681/healthz', timeout=2)"]
# Recarrega ao salvar; o depurador interativo do Werkzeug fica DESLIGADO (é um console de execução).
# A saída do processo (inclusive erros de importação após salvar) também vai para /tmp/app.log.
CMD ["sh", "-c", "python -u -m flask --app app run --host 0.0.0.0 --port 8080 --reload --no-debugger 2>&1 | tee -a /tmp/app.log"]
