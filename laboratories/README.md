# Laboratórios

Um diretório por laboratório: `manifest.yaml` (contrato `AppSecLab v1alpha1`), conteúdo e runtime da aplicação.
Validadores privados **não** ficam aqui.

| Diretório | Finalidade | Estado |
|---|---|---|
| `LAB-000-hello-benign` | Teste do motor, **sem vulnerabilidade** | Usado nos testes da 1ª fatia |

Validar localmente: `uv run python -m cecyber_contracts validate laboratories/<lab>/manifest.yaml`.
