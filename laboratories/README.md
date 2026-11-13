# Laboratórios

Um diretório por laboratório: `manifest.yaml` (contrato `AppSecLab v1alpha1`), conteúdo e runtime da aplicação.
Validadores privados **não** ficam aqui.

| Diretório | Finalidade | Estado |
|---|---|---|
| `LAB-000-hello-benign` | Teste do motor, **sem vulnerabilidade** | Usado nos testes da 1ª fatia |
| `LAB-001-sqli-clinica` | SQL Injection, Clínica VidaPlena (Flask) | 1.0.1 aprovada pelo PO, só local |
| `LAB-002-idor-banco` | IDOR, Banco Vértice Digital (Flask) | 1.0.0 em teste do PO, só local |
| `LAB-003-jwt-cartoes` | JWT sem verificação, Orbe Cartões (Node.js) | 1.0.0 em teste do PO, só local |
| `LAB-004-cmdi-industria` | Command Injection, Ferrara Metais (Flask, CLPs simulados) | 1.0.0 em teste do PO, só local; G5 antes de outro ambiente |
| `_base/python`, `_base/node` | Imagens base com o agente de workspace (arquivos + terminal) | Só local (ADR-008/015) |

Validar localmente: `uv run python -m cecyber_contracts validate laboratories/<lab>/manifest.yaml`.
