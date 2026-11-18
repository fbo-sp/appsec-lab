# AVISO-2026-031 · relatorix: leitura de arquivos fora da pasta de modelos

**Emitido por:** Time de Segurança de Produtos da Corretora Altiva Investimentos · **Severidade:** alta · **Data:** 10/11/2026

## Resumo

As versões **até a 2.4.0** da biblioteca `relatorix` não conferem se o modelo pedido fica dentro da
pasta de modelos. Um nome de modelo com `../`, inclusive na forma codificada (`%2e%2e%2f`), faz o
gerador ler e devolver arquivos de fora da pasta, como arquivos de configuração.

## Versões afetadas e corrigidas

| Versão | Situação |
| --- | --- |
| 2.1.0 a 2.4.0 | **Afetadas** |
| 2.4.1 | Corrigida |

## O que fazer

1. Procure `relatorix` no inventário de dependências (SBOM) de cada sistema.
2. Atualize o pin para `relatorix==2.4.1` no `requirements.txt` e publique.
3. **Não** tente contornar com filtros de texto no código da aplicação: a biblioteca decodifica o
   nome por conta própria, então o filtro vê uma coisa e a biblioteca abre outra.

Prazo para sistemas expostos à internet: **7 dias**.
