# Instruções para Codex e outros agentes de desenvolvimento

## Fonte de verdade e ordem de leitura

1. `docs/00_PRODUCT_VISION.md`
2. `docs/02_PRD.md`
3. `docs/07_THREAT_MODEL.md` e `docs/06_SYSTEM_ARCHITECTURE.md`
4. Especificação específica do componente, backlog e ADRs.

## Regras de atuação

- Responder e documentar em português brasileiro, salvo convenções de código e APIs.
- Antes de codificar, identificar requisito (FR/NFR), história do backlog, critérios de aceite e testes afetados.
- Não inventar decisões de produto nem transformar propostas em fatos; registrar perguntas abertas e recomendações em ADR.
- Fazer alterações incrementais e manter esquemas e contratos versionados.
- Não misturar plano de controle com plano de execução dos laboratórios.
- **Nunca** colocar credenciais do controle, tokens permanentes, socket Docker do host ou validadores secretos dentro dos sandboxes dos alunos.
- Negar acesso por padrão entre sessões e à infraestrutura administrativa, incluindo metadados cloud e rede interna.
- Tratar código submetido pelo aluno como **não confiável**, inclusive no processo de avaliação.
- Provisionamento e limpeza devem ser idempotentes e auditáveis; respeitar TTL, quotas e estados.
- Não publicar laboratórios ofensivos em infraestrutura exposta sem avaliação de isolamento, egress e testes adversariais.
- Não remover testes nem afrouxar políticas para fazê-los passar.
- Para cada incremento: especificar mudança, implementar, executar testes, registrar resultados e atualizar documentação/ADR.

## Qualidade esperada

- Preferir monólito modular para controle e separação lógica/física do runtime e dos runners.
- Autorização sempre no servidor, checando ownership por requisição e WebSocket.
- Idempotência nas APIs de criação, reset e avaliação; concorrência controlada.
- Feedback ao aluno não pode expor testes ocultos nem segredos.
- Não associar identificação ou nota ao status operacional transitório sem persistência.
- Requisitos de observabilidade, limpeza e segurança fazem parte do Definition of Done.

## Início recomendado

Primeiro revisar `docs/03_FUNCTIONAL_REQUIREMENTS.md`, `docs/04_NON_FUNCTIONAL_REQUIREMENTS.md`, `docs/07_THREAT_MODEL.md`, `docs/08_LAB_ENGINE_SPEC.md` e `docs/11_LAB_MANIFEST_SPEC.md`. Em seguida construir PoCs controladas antes de integrar UI ou lançar piloto.

## Diretrizes v0.3

Nome oficial: CECyber AppSec Labs. Hospedagem inicial on-premises (`docs/ADR/ADR-004-on-premises-hosting.md`). Implementar UX guiada por etapas e seis princípios `LEX-001` a `LEX-006` em `docs/21_LEARNING_EXPERIENCE_SPEC.md`. O passo seguinte nunca é desbloqueado pelo frontend e validadores não são acessíveis no workspace do aluno. O contrato de variantes é obrigatório mesmo com apenas uma variante publicada por laboratório no MVP.
