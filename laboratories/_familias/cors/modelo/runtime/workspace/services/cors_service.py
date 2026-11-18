"""Camada de serviço: a configuração de CORS da API. É AQUI que mora a falha deste laboratório.

CORS (Cross-Origin Resource Sharing) decide quais SITES (origens) podem ler, pelo navegador, a
resposta da nossa API. O cabeçalho `Access-Control-Allow-Origin` diz qual origem está liberada; com
`Access-Control-Allow-Credentials: true`, a leitura vale até com o cookie de sessão do usuário.

A falha: este serviço **reflete de volta qualquer origem** que chegar na requisição. Ou seja, um site
malicioso que a vítima visite pode ler, pelo navegador dela, os dados da API autenticada — porque a
API responde "sim, a sua origem está liberada" para qualquer um. A defesa é liberar só origens
confiáveis, de uma lista conhecida.
"""


class CorsService:
    def cabecalhos(self, origem: str) -> dict[str, str]:
        """Monta os cabeçalhos CORS da resposta da API, a partir da origem que veio na requisição."""
        if not origem:
            return {}
        # Reflete a origem recebida, seja ela qual for, e ainda libera o envio de credenciais.
        return {
            "Access-Control-Allow-Origin": origem,
            "Access-Control-Allow-Credentials": "true",
        }
