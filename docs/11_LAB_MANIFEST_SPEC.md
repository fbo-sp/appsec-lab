# 11. Contrato de Manifestos de Laboratório

| Campo | Valor |
|---|---|
| Produto | CECyber AppSec Labs |
| Versão | 0.3.0 |
| Estado | Proposta para revisão técnica, sem aprovação formal |
| Dependências | `02_PRD.md`, `08_LAB_ENGINE_SPEC.md`, `10_VALIDATION_ENGINE_SPEC.md`, `21_LEARNING_EXPERIENCE_SPEC.md` |

## 1. Princípios

Um **laboratório conceitual** representa **uma única vulnerabilidade-alvo** (preferencialmente uma CWE principal) com narrativa, objetivos e sequência de passos. Pode conter múltiplas **variantes de linguagem/runtime**, mas preserva os mesmos objetivos pedagógicos. O motor nunca precisa conhecer o ID de uma vulnerabilidade para executá-la. Toda publicação tem `lab_id`, `version` e digest imutáveis.

- `Lab`: conceito e roteiro independentes da linguagem.
- `LabVariant`: implementação por linguagem/framework com imagem OCI, comandos e políticas específicas.
- `LabStep`: etapa ordenada, com instruções, validação e dicas progressivas.
- `ValidatorRef`: referência a pacote de testes privados, **nunca enviado ao aluno**.
- `LabRelease`: snapshot imutável de todos os itens acima.

## 2. Esquema YAML ilustrativo v1alpha1

```yaml
apiVersion: labs.cecyber.io/v1alpha1
kind: AppSecLab
metadata:
  id: LAB-001
  version: 1.0.0
  title: SQL Injection em consulta de pedidos
  status: draft
  primaryCwe: CWE-89
  secondaryCwes: []
learning:
  singleVulnerability: true
  estimatedMinutes: 25
  difficulty: beginner
  objectives:
    - Reconhecer concatenação insegura em consultas SQL
    - Implementar parâmetros SQL mantendo a funcionalidade
  story:
    role: Desenvolvedor de uma plataforma de pedidos
    application: Serviço de consulta de pedidos da Loja Aurora (fictícia)
    context: Auditoria identificou acesso indevido a registros
    mission: Reproduzir o comportamento e corrigir o código
variants:
  - id: python-flask
    language: python
    framework: flask
    image: registry.interno/labs/sqli-python@sha256:REPLACE_WITH_REAL_DIGEST
    runtimeProfile: web-app
    workspacePath: /workspace
    startup:
      command: ["python", "app.py"]
      port: 5000
    build:
      command: ["python", "-m", "compileall", "-q", "/workspace"]
      timeoutSeconds: 20
    resources:
      cpuMillicores: 500
      memoryMiB: 512
      storageMiB: 512
    session:
      ttlMinutes: 45
    interfaces: [editor, terminal, web]
steps:
  - id: inspect
    order: 1
    title: Investigar a consulta
    explanation: Identifique onde dados do usuário são incorporados à query
    task: Localize a função que recebe o identificador do pedido
    concept: Consultas SQL parametrizadas
    validatorRef: sqli/python-flask/inspect-v1
    hints:
      - level: 1
        text: Observe o endpoint de consulta
      - level: 2
        text: Procure a construção da query
      - level: 3
        text: Inspecione o arquivo orders_repository.py próximo à consulta
    unlockOnPass: true
    points: 20
  - id: exploit
    order: 2
    title: Demonstrar a falha
    explanation: Use somente o alvo efêmero do exercício
    task: Confirme acesso a registro de teste que não pertence ao usuário
    validatorRef: sqli/python-flask/exploit-v1
    unlockOnPass: true
    points: 30
  - id: remediate
    order: 3
    title: Corrigir e testar
    explanation: A correção deve bloquear injeção sem quebrar buscas válidas
    task: Substitua concatenação por parâmetros e rode os testes
    validatorRef: sqli/python-flask/fix-v1
    unlockOnPass: true
    points: 50
policy:
  sequentialUnlock: true
  allowStepRetry: true
  persistProgressAcrossReset: true
  allowSolutionReveal: false
  finalPassingScore: 70
```

**Nota:** o digest de exemplo é um placeholder proposital, não uma imagem publicável. Para o MVP, uma variante por lab é suficiente; a estrutura já suporta várias. A ordem das etapas é declarativa e a autorização para avançar sempre é decidida pelo backend.

## 3. Regras de consistência

1. `apiVersion` deve estar numa allowlist do motor; rejeitar campos desconhecidos críticos.
2. `metadata.id` e `variants[].id` são estáveis; (`id`, `version`) é único.
3. `primaryCwe` válido e narrativa, aplicação e missão obrigatórias.
4. Cada etapa possui ID e ordem únicos, instrução, explicação, `validatorRef` e pontuação não negativa.
5. Cada dica usa nível único e possui conteúdo; liberar por solicitação e registrar uso.
6. Cada `validatorRef` precisa existir no registro protegido de validadores e ser compatível com variante e versão.
7. Imagens publicadas devem ser referenciadas por digest real, escaneadas, aprovadas e assinadas conforme política.
8. Comandos devem seguir política de execução; não aceitar shells arbitrários de manifestos não confiáveis no plano de controle.
9. As variantes devem mapear o **mesmo objetivo pedagógico** para validadores equivalentes; não presumir que testes binários sejam idênticos.
10. Publicação é atômica e gera assinatura/digest da release; releases anteriores não mudam.

## 4. Separação de conteúdo e runtime

`content/pt-BR/*.md` pode guardar storytelling, conceitos, passos e dicas em arquivos versionados, referenciados no manifesto em vez de embutidos. `runtime/<variant>/` inclui a aplicação realista e dados fictícios. `validation/<variant>/` fica em distribuição **separada** com controle de acesso, nunca dentro da imagem disponibilizada ao aluno. A interface web deve permitir editar, compilar, pré-compilar, interpretar e reiniciar conforme a tecnologia; o motor expõe uma operação de `build` ou `run` parametrizada por comandos aprovados.

## 5. Pipeline mínimo de publicação

Lint YAML -> validação JSON Schema -> validação semântica -> build OCI -> SCA/scan -> teste de execução isolada -> suíte de avaliação positiva/negativa -> verificação de storytelling e dicas -> assinatura -> publicação. Falha em qualquer gate bloqueia `published`.

## 6. Casos de teste

- Duas variantes do mesmo lab exibem os mesmos passos e objetivos, mas abrem runtimes diferentes.
- Versão não pode ser sobrescrita após `published`.
- Falha de validador não desbloqueia etapa.
- Tentativa de publicar imagem sem digest válido ou validador ausente é rejeitada.
- Alterar texto ou dica após publicação exige nova versão.

## 7. Pendências

Definir política de pontuação por dicas, nível de detalhamento de soluções e se `build` aceita scripts definidos pelo autor técnico ou somente perfis previamente aprovados. Registro em ADR obrigatório antes da implementação.
