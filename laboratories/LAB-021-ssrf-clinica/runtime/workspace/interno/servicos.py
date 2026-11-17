"""Serviços internos SIMULADOS, que sobem junto com a aplicação (ADR-008), só em loopback.

Eles representam dois sistemas internos da rede da Clínica Sampaio:

    127.0.0.1:8090  -> Serviço de Documentos (o destino LEGÍTIMO do importador)
    127.0.0.1:9000  -> Console de Infraestrutura (uso interno; guarda credenciais)

Nenhum dos dois é exposto para fora da sessão. Eles NÃO fazem parte da lição de código: estão
aqui só para o importador ter o que buscar. A falha a corrigir está em services/importador_service.py.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Conteúdo que o Serviço de Documentos devolve (documento fictício do domínio).
_DOCUMENTO = """LAUDO DE EXAME (documento fictício — laboratório parceiro Sampaio)
Paciente: Rafael Antunes Barreto
Exame: Hemograma completo
Resultado: dentro dos valores de referência
Laudo liberado pelo parceiro em 2026-11-10.
"""

# Credenciais fictícias que o Console de Infraestrutura guarda (uso interno). NÃO são reais.
_CREDENCIAIS = {
    "servico": "integracao-laboratorio",
    "chave_integracao": "CHAVE-FICTICIA-SAMPAIO-NAO-USAR",
    "aviso": "uso interno — nao exponha",
}


class _Documentos(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (nome exigido pelo http.server)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(_DOCUMENTO.encode("utf-8"))

    def log_message(self, *_: object) -> None:
        pass


class _Console(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (nome exigido pelo http.server)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(_CREDENCIAIS, ensure_ascii=False).encode("utf-8"))

    def log_message(self, *_: object) -> None:
        pass


def iniciar() -> None:
    """Sobe os dois serviços internos em threads de fundo (só loopback).

    Com o --reload do Flask o módulo é importado em mais de um processo; quem conseguir a porta
    primeiro mantém o serviço no ar, e os demais apenas seguem adiante (a porta já está escutando).
    """
    for port, handler in ((8090, _Documentos), (9000, _Console)):
        try:
            servidor = ThreadingHTTPServer(("127.0.0.1", port), handler)
        except OSError:
            continue  # já está no ar (ex.: processo pai do reloader)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
