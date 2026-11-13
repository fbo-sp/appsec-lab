# Imagem do LAB-004 (OS Command Injection, Flask) para o runtime Docker LOCAL (ADR-008).
# CONTÉM VULNERABILIDADE INTENCIONAL: usar só em rede interna da sessão, nunca exposta (ver ADR-008).
# A injeção executa comandos DENTRO do contêiner da sessão, com o mesmo usuário sem privilégios
# (10001), sem capabilities e sem rede externa: o mesmo alcance que o terminal do aluno já tem.
# Build: scripts/lab-local.sh (ou scripts/lab-local.ps1 no Windows), que antes constrói a base.
FROM cecyber-labs/base-python:local

USER root
RUN pip install --no-cache-dir "flask==3.1.2"
# Planta SIMULADA: utilitário de diagnóstico e arquivos fictícios fora do workspace.
# sed: defesa contra checkout com CRLF (Windows), que quebraria o shebang do utilitário.
COPY planta/diag-clp.py /usr/local/bin/diag-clp
COPY planta/equipamentos.csv planta/scada.conf /opt/planta/
RUN sed -i 's/\r$//' /usr/local/bin/diag-clp /opt/planta/equipamentos.csv /opt/planta/scada.conf \
 && chmod 0755 /usr/local/bin/diag-clp && chmod 0755 /opt/planta && chmod 0644 /opt/planta/*
USER 10001

# Conteúdo inicial do workspace: copiado para o volume da sessão na primeira montagem.
COPY --chown=10001:10001 workspace/ /workspace/
EXPOSE 8080
# Pronto = aplicação (8080) e agente de workspace (7681) respondendo.
HEALTHCHECK --interval=3s --timeout=10s --start-period=3s --retries=20 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/diagnostico', timeout=2); u.urlopen('http://127.0.0.1:7681/healthz', timeout=2)"]
# Recarrega ao salvar; o depurador interativo do Werkzeug fica DESLIGADO (é um console de execução).
# A saída do processo (inclusive erros de importação após salvar) também vai para /tmp/app.log.
CMD ["sh", "-c", "python -u -m flask --app app run --host 0.0.0.0 --port 8080 --reload --no-debugger 2>&1 | tee -a /tmp/app.log"]
