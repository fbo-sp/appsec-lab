"""Camada de serviço: como a API responde quando algo dá errado. É AQUI que mora a falha.

Quando o processamento falha, a aplicação precisa responder ao cliente. A pergunta de SEGURANÇA é:
quanto contar? Este serviço devolve, na resposta ao cliente, a mensagem interna da exceção E o
traceback completo — que expõe caminhos de arquivos, nomes internos e pistas da tecnologia usada.
Isso é um prato cheio para quem ataca. A defesa é LOGAR o detalhe no servidor e devolver ao cliente
apenas uma mensagem genérica.
"""

import traceback


class ErroService:
    def resposta(self, exc: Exception) -> dict[str, str]:
        """Monta o corpo JSON de erro para devolver ao cliente."""
        # Expõe a mensagem interna e o traceback completo na resposta ao cliente.
        return {"erro": str(exc), "detalhe": traceback.format_exc()}
