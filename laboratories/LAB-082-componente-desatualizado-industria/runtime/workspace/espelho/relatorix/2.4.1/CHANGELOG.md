# relatorix: notas de versão

## 2.4.1

- **Segurança (AVISO-2026-031):** `Gerador.gerar` passa a conferir que o modelo fica dentro da pasta
  de modelos, depois de decodificar o nome e resolver `..`, links e caminhos absolutos. Nas versões
  até a 2.4.0, um nome de modelo como `../config/arquivo.ini` (ou a forma codificada `%2e%2e%2f`)
  lia arquivos de fora da pasta.
- Mensagem de erro de modelo inexistente não mostra mais o nome pedido.

## 2.3.0

- Novo campo `$data_emissao` disponível em todos os modelos.

## 2.2.0

- Suporte a modelos com acentos no nome do arquivo.

## 2.1.0

- Primeira versão usada pelos sistemas internos.
