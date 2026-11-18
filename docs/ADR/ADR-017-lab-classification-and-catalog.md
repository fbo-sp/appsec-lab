# ADR-017: Classificação dos laboratórios e catálogo com histórico de versões

- **Status:** Aceito pelo PO (2026-11-15).
- **Data:** 2026-11-15
- **Relacionados:** ADR-006 (releases imutáveis), ADR-012 (conteúdo), ADR-016 (painel com a última versão), `docs/11_LAB_MANIFEST_SPEC.md`, `docs/17_MVP_LAB_CATALOG.md`

## Contexto

A CECyber escolhe o laboratório de cada aula conceitual pela classificação da falha. O PO pediu (2026-11-15) que todo lab, além do CWE, seja classificado no OWASP Top 10 mais atual e na edição anterior e no SANS CWE Top 25; quando não se enquadrar, o CWE orienta. Pediu também um catálogo em arquivo, mantido na documentação e atualizado a cada lab ou versão nova, com as versões antigas e as datas em que foram criadas e ficaram obsoletas, e a classificação na página de abertura de cada lab, num bloco ao final.

## Decisão

1. **Manifesto:** campo opcional `metadata.classifications`, lista de `{framework, edition, entries}`. Uma entrada por lista **e** por edição. Quando há mais de um item, o texto marca o principal. O campo é opcional e sem valor padrão serializado, então os digests de releases existentes não mudam.
2. **Listas e edições (nov/2026, conferidas em owasp.org e cwe.mitre.org):** OWASP Top 10 2025 e 2021; OWASP API Security Top 10 2023 e 2019 quando o lab é de API; SANS CWE Top 25 2025 e 2024 (nome adotado pela CECyber para a lista CWE Top 25, publicada pela MITRE com a CISA e criada com a SANS).
3. **LAB-003:** categoria principal A07 Authentication Failures, com A04 Cryptographic Failures como secundária (decisão do PO por card, 2026-11-15). O mapeamento oficial do CWE-347 é A04, mas o lab ensina um desvio de autenticação.
4. **Portal:** a página de abertura mostra, por último, o bloco "Classificação" com CWE e uma linha por lista e edição.
5. **Catálogo:** `docs/catalogo/CATALOGO_DE_LABORATORIOS.md` é gerado por `scripts/gen-catalogo.py` a partir dos manifestos e de `docs/catalogo/historico-versoes.yaml`, que guarda versão, data de publicação e resumo da mudança. A data de obsolescência é a data de publicação da versão seguinte. O CI roda `gen-catalogo.py --check` e falha se a versão de algum manifesto não estiver no histórico ou se o catálogo estiver desatualizado. O LAB-000, benigno, aparece numa seção de uso interno.
6. **Versões:** LAB-001 1.0.2, LAB-002 1.0.2, LAB-003 1.0.1 e LAB-004 1.0.2 trazem a classificação e trocam as referências do OWASP Top 10 de 2021 para 2025. Etapas, respostas e suítes de correção não mudaram.

## Consequências

- Professores e área comercial têm um arquivo único e sempre em dia; o histórico vem do repositório, não do banco local, que pode ser recriado.
- As datas são de publicação no repositório (ambiente local). Quando houver implantação, valerá a data de publicação nela.
- Novas edições das listas exigem revisar a classificação e publicar versões novas dos labs.
- Testes: `test_classifications_*` (contrato), `test_public_view_exposes_classifications` (API) e a verificação do catálogo no CI.
