# [[app_nome]] · [[empresa]] (ambiente de treinamento)

Aplicação de treinamento do CECyber AppSec Labs. **Todos os dados são fictícios** e ela contém, de
propósito, um **componente com falha conhecida** (OWASP A06:2021, A03:2025) para você encontrar e
corrigir.

## Como ela está organizada

```
navegador -> controllers/ -> services/ -> repositories/ -> banco SQLite
                 |               |
                 |               +-> relatorix (biblioteca de documentos, versão em requirements.txt)
                 +-> templates/  (monta o HTML de resposta)
```

- `requirements.txt` — as dependências e a versão fixada de cada uma. **É aqui que se corrige.**
- `sbom.json` — o inventário de componentes (SBOM, formato CycloneDX) deste sistema.
- `avisos/` — avisos de segurança do time de segurança de produtos.
- `espelho/` — o espelho interno de pacotes (o laboratório não tem internet); `dependencias.py`
  carrega daqui a versão fixada em `requirements.txt`.
- `services/documento_service.py` — monta o [[documento_nome]] para impressão com a relatorix.
- `modelos/` — os modelos HTML do documento.

## A feature

O cliente escolhe um modelo e gera o [[documento_nome]] para impressão. O nome do modelo vai para a
biblioteca relatorix, que abre o arquivo da pasta `modelos/` e preenche os campos. A versão fixada
da biblioteca tem uma falha publicada: ela não confere se o modelo fica dentro da pasta.
