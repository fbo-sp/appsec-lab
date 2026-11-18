# ADR-016: Catálogo mostra só a última versão de cada laboratório

- **Status:** Aceito pelo PO (2026-11-14).
- **Data:** 2026-11-14
- **Relacionados:** ADR-006 (releases imutáveis), ADR-008, `docs/11_LAB_MANIFEST_SPEC.md`

## Contexto

Releases são imutáveis: qualquer ajuste de texto ou código de um laboratório gera uma versão nova. Durante os testes do PO, versões antigas (LAB-001 1.0.0, LAB-004 1.0.0, LAB-002 1.0.0) continuavam no painel ao lado das corrigidas, o que confundia e exigia retirá-las à mão no banco. O PO pediu (2026-11-14): "manter apenas a última versão dos laboratórios no painel. Isso facilita os testes".

## Decisão

- `GET /api/v1/labs` devolve, para cada laboratório, apenas a release **publicada de versão SemVer mais alta** (não a mais recente por data de registro).
- Versões anteriores **não são retiradas nem apagadas**: continuam publicadas e acessíveis por `GET /api/v1/labs/{lab}/releases/{versão}`, para que tentativas e sessões já iniciadas nelas sigam funcionando.
- Retirar uma versão (status `retired`) continua sendo uma ação explícita, para quando ela não deve mais ser usada nem por endereço.

## Consequências

- Publicar uma versão nova a substitui no painel sem passo manual.
- Não é possível oferecer duas versões do mesmo lab lado a lado no painel. Quando houver turmas (IMP-204), a atribuição poderá fixar uma versão específica.
- Teste: `test_catalog_lists_only_latest_version` (inclui ordem de registro trocada e comparação SemVer `0.10.0 > 0.3.0`).
