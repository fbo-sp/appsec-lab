"""SIMULA o serviço de integridade da loja de apps (Play Integrity no Android, App Attest no iOS).

Este arquivo NÃO tem falha e não precisa ser alterado.

Como o serviço real funciona: o app pede um **selo** ao sistema do celular; a loja confere se o
pacote instalado é o publicado por ela, sem modificações e assinado pela empresa, e devolve um selo
**assinado pela loja** com o veredito, a conta e a validade. O app só repassa o selo ao servidor, que
o confere. O app não consegue fabricar um selo válido, porque não tem a chave de assinatura da loja.

Como a simulação funciona: em vez de conferir a assinatura de um APK, o serviço calcula o hash do
código do app (``static/app.js`` e ``static/regras.js``) e compara com o hash do pacote oficial,
registrado quando a imagem foi construída, numa pasta fora do workspace (``/opt/loja``). A chave do
selo também fica lá. Se o código do app foi alterado, o veredito é ``app_modificado``.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import time

logger = logging.getLogger("atestacao")

ARQUIVOS_DO_APP = ("static/app.js", "static/regras.js")


class AtestacaoService:
    VALIDADE_SEGUNDOS = 120

    def __init__(self, pasta_loja: str, pasta_app: str) -> None:
        self._pasta_loja = pasta_loja
        self._pasta_app = pasta_app

    def _ler_loja(self, nome: str) -> str:
        with open(os.path.join(self._pasta_loja, nome), encoding="utf-8") as arquivo:
            return arquivo.read().strip()

    def _hash_do_app(self) -> str:
        h = hashlib.sha256()
        for relativo in ARQUIVOS_DO_APP:
            with open(os.path.join(self._pasta_app, relativo), "rb") as arquivo:
                h.update(arquivo.read())
        return h.hexdigest()

    def _assinar(self, corpo: str) -> str:
        chave = self._ler_loja("chave").encode()
        return hmac.new(chave, corpo.encode(), hashlib.sha256).hexdigest()

    def emitir(self, conta_id: int) -> str:
        """A "loja" confere o código do app e devolve um selo assinado com o veredito."""
        oficial = self._hash_do_app() == self._ler_loja("pacote_oficial.sha256")
        veredito = "app_oficial" if oficial else "app_modificado"
        dados = {"conta_id": conta_id, "veredito": veredito, "expira_em": int(time.time()) + self.VALIDADE_SEGUNDOS}
        corpo = base64.urlsafe_b64encode(json.dumps(dados, sort_keys=True).encode()).decode()
        logger.info("Selo emitido: conta=%s veredito=%s", conta_id, veredito)
        return f"{corpo}.{self._assinar(corpo)}"

    def verificar(self, selo: object, conta_id: int) -> bool:
        """True só se o selo foi assinado pela loja, é desta conta, diz app_oficial e não venceu."""
        if not isinstance(selo, str) or selo.count(".") != 1:
            return False
        corpo, assinatura = selo.split(".")
        if not hmac.compare_digest(self._assinar(corpo), assinatura):
            return False  # selo forjado ou alterado
        try:
            dados = json.loads(base64.urlsafe_b64decode(corpo.encode()))
        except ValueError:
            return False
        return (
            dados.get("conta_id") == conta_id
            and dados.get("veredito") == "app_oficial"
            and int(dados.get("expira_em", 0)) > time.time()
        )
