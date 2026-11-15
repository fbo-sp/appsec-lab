# Laboratórios

Um diretório por laboratório: `manifest.yaml` (contrato `AppSecLab v1alpha1`), conteúdo e runtime da aplicação.
Validadores privados **não** ficam aqui.

| Diretório | Finalidade | Estado |
|---|---|---|
| `LAB-000-hello-benign` | Tutorial da plataforma (sem vulnerabilidade) | 1.0.0, só local (ADR-018) |
| `LAB-001-sqli-clinica` | SQL Injection, Clínica VidaPlena (Flask) | 1.0.2 (classificação; conteúdo da 1.0.1 aprovado pelo PO), só local |
| `LAB-002-idor-banco` | IDOR, Banco Vértice Digital (Flask) | 1.0.2 em teste do PO, só local |
| `LAB-003-jwt-cartoes` | JWT sem verificação, Orbe Cartões (Node.js) | 1.0.1 em teste do PO, só local |
| `LAB-004-cmdi-industria` | Command Injection, Ferrara Metais (Flask, CLPs simulados) | 1.0.2 em teste do PO, só local; G5 antes de outro ambiente |
| `_base/python`, `_base/node` | Imagens base com o agente de workspace (arquivos + terminal) | Só local (ADR-008/015) |

Validar localmente: `uv run python -m cecyber_contracts validate laboratories/<lab>/manifest.yaml`.

Ao criar um lab ou publicar uma versão nova: preencha `metadata.classifications`, acrescente a versão em `docs/catalogo/historico-versoes.yaml` e rode `uv run python scripts/gen-catalogo.py` para atualizar o [catálogo](../docs/catalogo/CATALOGO_DE_LABORATORIOS.md) (ADR-017; o CI falha se esquecer).
