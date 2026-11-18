# Imagem do [[lab_id]] ([[codigo]]: Cross-Site Request Forgery, Flask + SQLite) para o runtime Docker LOCAL (ADR-008).
# CONTÉM VULNERABILIDADE INTENCIONAL: usar só em rede interna da sessão, nunca exposta (ver ADR-008).
# Gerado por scripts/gerar-familia.py a partir de laboratories/_familias/csrf (ADR-021).
FROM cecyber-labs/base-python:local

USER root
RUN pip install --no-cache-dir "flask==3.1.2"
# Página FICTÍCIA do atacante (ADR-022): servida na porta 8090 e publicada pelo gateway em outra origem.
# Fica fora do workspace: o aluno não precisa editá-la, só abrir e ler.
COPY atacante/ /opt/atacante/
USER 10001

# Conteúdo inicial do workspace: copiado para o volume da sessão na primeira montagem.
COPY --chown=10001:10001 workspace/ /workspace/
EXPOSE 8080 8090
# Pronto = aplicação (8080), site do atacante (8090) e agente de workspace (7681) respondendo.
HEALTHCHECK --interval=3s --timeout=10s --start-period=3s --retries=20 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/login', timeout=2); u.urlopen('http://127.0.0.1:8090/', timeout=2); u.urlopen('http://127.0.0.1:7681/healthz', timeout=2)"]
# Recarrega ao salvar; o depurador interativo do Werkzeug fica DESLIGADO (é um console de execução).
# A saída do processo (inclusive erros de importação após salvar) também vai para /tmp/app.log.
CMD ["sh", "-c", "python -m http.server 8090 -b 0.0.0.0 -d /opt/atacante >/dev/null 2>&1 & python -u -m flask --app app run --host 0.0.0.0 --port 8080 --reload --no-debugger 2>&1 | tee -a /tmp/app.log"]
