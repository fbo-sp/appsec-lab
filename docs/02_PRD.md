# 02. PRD | Product Requirements Document

| Campo | Valor |
|---|---|
| Produto | CECyber AppSec Labs |
| Versão | 0.1.0 |
| Estado | Rascunho estruturado para refinamento e aprovação |
| Data | 2026-11-11 |
| Documento de referência | `00_PRODUCT_VISION.md` |
| Release alvo | MVP, quatro laboratórios e piloto controlado |

## 1. Objetivo e contexto

Descrever o comportamento esperado do MVP de uma plataforma de treinamento prático que executa aplicações vulneráveis em ambientes individuais e avalia automaticamente atividades de exploração e remediação. O documento orientará arquitetura, backlog, implementação assistida por agentes, QA e homologação. Não detalha toda a implementação interna: estas decisões pertencem às especificações técnicas e ADRs.

**Princípio crítico:** as operações perigosas dos laboratórios são confinadas ao plano de execução; autorização, catálogo, resultados e avaliação confiável não devem depender da integridade do workspace do aluno.

## 2. Resultado esperado e não objetivos

**Resultado:** um usuário autorizado consegue selecionar um dos quatro laboratórios, criar uma sessão isolada, executar a aplicação, editar código, utilizar terminal, completar objetivos, receber feedback e consultar seu progresso; um instrutor consegue visualizar resultados; um operador consegue monitorar e encerrar sessões.

**Não objetivos P0:** editor visual de laboratório, marketplace, cobrança, CTF competitivo, IA tutora, ambientes Windows/AD, LTI 1.3 completo, multi-tenancy empresarial, execução de alvos externos, laboratórios cooperativos.

## 3. Perfis, limites e permissões

| Perfil | Catálogo | Iniciar lab | Editar workspace | Avaliar | Ver resultados | Administrar sessões | Publicar |
|---|---|---|---|---|---|---|---|
| Aluno | Autorizados | Próprios | Próprios | Próprios | Próprios | Reset próprio limitado | Não |
| Instrutor | Turmas atribuídas | Opcional como aluno | Próprios | Próprios | Turmas atribuídas | Solicitar intervenção / visão limitada | Não |
| Administrador | Todos | Sim | Só via sessão autorizada | Sim | Conforme política e auditoria | Sim | Sim, via pipeline |
| Autor técnico (função de pipeline) | Conteúdo versionado | Prévia homologação | Ambiente de teste | Suite de testes | Teste/publicação | Não necessariamente | Por aprovação e CI/CD |

RBAC deve ser combinado com **ownership** e **escopo de turma**. Não basta verificar o papel no frontend. Toda URL, chamada REST, WebSocket e acesso por gateway precisa aplicar autorização no servidor. Um instrutor não terá automaticamente acesso ao terminal dos alunos.

## 4. Vocabulário e modelo conceitual

| Termo | Definição |
|---|---|
| Laboratory | Especificação pedagógica e técnica identificada por ID |
| LaboratoryVersion | Versão imutável de conteúdo, imagem, configuração e suite de avaliação |
| Enrollment / Assignment | Vínculo que autoriza aluno a executar um lab (individual ou por turma) |
| Session | Instância lógica iniciada pelo aluno, com estado e TTL |
| RuntimeInstance | Recurso efêmero que hospeda o sandbox da sessão |
| Workspace | Arquivos editáveis e terminal dentro da sessão |
| Attempt | Submissão do aluno para avaliação em uma revisão consistente do workspace |
| EvaluationRun | Execução assíncrona, protegida e rastreável dos validadores para uma tentativa |
| Result | Pontuação, critérios, feedback e evidências associadas à tentativa |
| Completion | Estado acadêmico de conclusão, separado da disponibilidade do runtime |

Uma `Session` não equivale a `Attempt`: o aluno pode submeter várias tentativas durante uma sessão. Uma mesma versão de laboratório pode ser iniciada novamente conforme política de atribuição.

## 5. Jornada ponta a ponta (happy path)

1. Login OIDC e perfil carregado no backend.
2. Listagem de laboratórios publicados e atribuídos.
3. Abertura da página de detalhes, objetivos e limites.
4. Solicitação de início com chave de idempotência.
5. Session Manager cria `REQUESTED` e inicia provisionamento assíncrono.
6. Runtime atinge `READY`; gateway autentica WebSocket/HTTP e oferece editor, terminal e aplicação.
7. Aluno interage com a aplicação e altera arquivos.
8. Solicita avaliação; API cria `Attempt` e `EvaluationRun` apontando para revisão estável do workspace.
9. Runner confiável executa testes positivos, negativos e regressão; devolve resultado assinado/autenticado ao controle.
10. Backend calcula pontuação e conclusão conforme política versionada.
11. Aluno recebe feedback e, se necessário, corrige e envia nova tentativa.
12. Ao concluir ou expirar, sessão é encerrada, runtime destruído e histórico mantido.
13. Instrutor acompanha desempenho e exporta CSV.

## 6. Catálogo de requisitos funcionais

### 6.1 Identidade e autorização

**FR-001 (P0) Autenticação:** usuários acessam o portal por OIDC, com sessão e expiração definidas; logout encerra autorização ativa.

**FR-002 (P0) Autorização por recurso:** cada operação em laboratório, sessão, tentativa, avaliação, log e conexão WebSocket checa papel, atribuição e proprietário.

**FR-003 (P0) Perfis:** papéis aluno, instrutor e administrador; autor técnico tratado via fluxo CI/CD.

**FR-004 (P0) Turmas e atribuições simples:** administrador vincula alunos a turmas e laboratórios; instrutor vê somente turmas autorizadas.

**Aceite do domínio:** aluno A não consegue listar/acessar sessão, arquivos, logs, avaliação ou URL de aluno B, inclusive por manipulação de IDs e reconexões WebSocket. Instrutor sem turma vinculada recebe negação.

### 6.2 Catálogo e publicação

**FR-010 (P0) Catálogo:** listar laboratórios disponíveis com título, resumo, tema, dificuldade, estimativa de tempo e estado publicado.

**FR-011 (P0) Manifesto validado:** cada laboratório descreve ID, versão, imagem imutável, runtime, recursos, interface, TTL, suite de testes e políticas de avaliação.

**FR-012 (P0) Publicação imutável:** novas versões não alteram sessões nem resultados de versões anteriores; invalidar artefatos em caso de risco é operação auditada.

**FR-013 (P0) Pipeline de qualidade:** publicação exige schema validado, build rastreável, checks de segurança e smoke tests.

**FR-014 (P1) Controle de visibilidade:** published/draft/retired por versão; drafts acessíveis somente a homologadores.

**Aceite do domínio:** publicar uma quinta versão de teste, ou atualizar um dos quatro labs, sem mudar código ou endpoint do motor; sessão antiga continua referenciando sua versão original.

### 6.3 Gestão de sessões

**FR-020 (P0) Criar sessão:** aluno inicia laboratório autorizado; solicitação retorna ID e status imediatamente, sem aguardar provisionamento.

**FR-021 (P0) Estados formais:** `REQUESTED`, `PROVISIONING`, `READY`, `ACTIVE`, `VALIDATING` (subestado/transição de avaliação), `COMPLETED`, `EXPIRED`, `FAILED`, `TERMINATING`, `TERMINATED`; definir transições e tratamento de timeout em especificação do motor.

**FR-022 (P0) Idempotência:** a mesma intenção de criar sessão, com chave estável, não cria múltiplos ambientes; requisições concorrentes não causam duplicidade.

**FR-023 (P0) Consultar e reconectar:** usuário acompanha estado e pode reconectar à própria sessão ativa sem receber novo runtime.

**FR-024 (P0) Reset:** solicitar restauração do workspace conforme política; progresso acadêmico e histórico anterior permanecem preservados; operação possui limite e auditoria.

**FR-025 (P0) TTL e expiração:** ambiente perde acesso ao expirar e é destruído pelo reconciliador, mesmo após falha de worker ou reinício de serviço.

**FR-026 (P0) Encerramento:** completar, desistir ou encerramento administrativo geram limpeza auditável.

**FR-027 (P0) Quotas:** limites por usuário, turma e total de sessões, além de CPU, RAM, processos e rede por runtime.

**Aceite do domínio:** testes de duplicidade, falha no provisionamento, restart do backend, reset em avaliação, expiração com WebSocket aberto e cleanup órfão.

### 6.4 Workspace e experiência

**FR-030 (P0) Interface web:** página de lab com instruções e progresso em etapas, indicador de estado e timer.

**FR-031 (P0) Editor:** abrir, modificar e salvar arquivos permitidos no workspace; arquivos e configurações sensíveis não editáveis.

**FR-032 (P0) Terminal:** terminal interativo associado apenas à instância autorizada, com limites de uso e logging operacional proporcional.

**FR-033 (P0) Prévia da aplicação:** aplicação web acessada por gateway com checagem de sessão e proteção contra host-header e roteamento arbitrário.

**FR-034 (P0) Feedback operacional:** exibir inicializando, pronto, falha recuperável, tempo expirado, validando e concluído.

**FR-035 (P1) Dicas e progresso:** exibir dicas versionadas e marcar etapas concluídas; registrar seu uso para análise pedagógica.

**Aceite do domínio:** editor, terminal e prévia funcionam sem instalação local; URLs de uma sessão não são utilizáveis por outra; tentativas de URL arbitrária ou acesso à rede administrativa são bloqueadas.

### 6.5 Avaliação e resultados

**FR-040 (P0) Submissão de tentativa:** aluno inicia avaliação de sua sessão ativa, recebendo identificador e estado de execução.

**FR-041 (P0) Snapshot consistente:** a avaliação utiliza revisão definida dos artefatos; evitar race condition com edição concorrente.

**FR-042 (P0) Runner confiável:** verificadores e segredos não residem no workspace editável; entrada do aluno é tratada como não confiável.

**FR-043 (P0) Validações:** suportar exploração, correção e regressão, com limites de tempo, recursos e saída; evitar avaliação baseada somente em string/padrão textual.

**FR-044 (P0) Pontuação:** computar nota determinística a partir de critérios e pesos da versão publicada; mínimo de aprovação por laboratório.

**FR-045 (P0) Histórico:** persistir tentativas, resultados, versão do laboratório, timestamps, estado e evidências minimizadas.

**FR-046 (P0) Feedback:** informar sucesso/falha por critério e orientação pedagógica, sem divulgar segredos ou testes ocultos.

**FR-047 (P0) Concorrência e repetição:** evitar avaliações conflitantes na mesma sessão; duplicatas com chave de idempotência não geram nota duplicada.

**FR-048 (P1) Política de nota consolidada:** melhor tentativa, última tentativa ou outro critério configurável por atividade (padrão proposto: melhor tentativa válida).

**Aceite do domínio:** solução correta aprovada; exploração incompleta ou correção que quebra função legítima rejeitada; alteração de arquivos da tentativa após snapshot não afeta resultado; resultado não pode ser falsificado pelo aluno.

### 6.6 Gestão, relatórios e operação

**FR-050 (P0) Visão do instrutor:** lista de alunos atribuídos e status por lab, melhor nota, tentativas e conclusão.

**FR-051 (P0) Exportação CSV:** identificar aluno, turma, lab, versão, status, nota e timestamps, com campos e política de privacidade definidos.

**FR-052 (P0) Visão do operador:** listar sessões, tempos, falhas, consumo e ações administrativas auditáveis.

**FR-053 (P0) Observabilidade:** logs estruturados com correlation_id, métricas de provisionamento, avaliações, falhas e limpeza.

**FR-054 (P1) API de resultados:** consulta autorizada para evolução futura do Moodle/LTI, com paginação e contrato versionado.

**Aceite do domínio:** instrutor não acessa turmas alheias; um ambiente destruído mantém os resultados; operador identifica instância órfã e acompanha sua remoção.

## 7. Requisitos não funcionais

| ID | Dimensão | Meta / obrigação preliminar | Forma de validação |
|---|---|---|---|
| NFR-001 | Isolamento | Zero acessos cruzados comprovados; sem acesso a host/controle | Testes adversariais e revisão de sandbox |
| NFR-002 | Rede | Negação padrão de egress e de acesso a serviços internos, DNS e metadados, exceto allowlist | Testes de política por sandbox |
| NFR-003 | Simultaneidade | 30 sessões ativas no piloto | Teste de carga representativo |
| NFR-004 | Inicialização | P95 <= 60 s em labs simples | Métrica REQUESTED → READY |
| NFR-005 | Provisionamento | >=98% das solicitações válidas atingem READY | Janela e amostra definidas no plano de testes |
| NFR-006 | Disponibilidade | Meta 99% nas janelas programadas do piloto | Monitoração do serviço e critérios de exclusão |
| NFR-007 | Limpeza | 100% das sessões expiradas entram em rotina de cleanup; prazo máximo a definir | Testes com falhas de worker/cluster |
| NFR-008 | Persistência | Resultados acadêmicos preservados após falha de runtime | Teste de recuperação |
| NFR-009 | Determinismo | Suítes de avaliação produzem resultados repetíveis | Reexecução controlada e testes adversariais |
| NFR-010 | Auditoria | Ações críticas rastreáveis a ator, sessão, resultado e horário | Inspeção de eventos e retenção |
| NFR-011 | Privacidade | Minimização, RBAC, retenção definida e descarte | Revisão LGPD e fluxo de dados |
| NFR-012 | Supply chain | Imagens imutáveis e rastreáveis; verificação de vulnerabilidades | Pipeline CI/CD |
| NFR-013 | Observabilidade | Correlação de API, sessão, workload e avaliação | Teste operacional ponta a ponta |
| NFR-014 | Segurança do gateway | WebSocket/HTTP com autenticação, expiração e autorização contínua | Testes IDOR, token e reconexão |
| NFR-015 | Portabilidade | Adaptação de runtime sem mudar contratos acadêmicos | PoC com mock adapter e contrato |

Metas a serem revisitadas após PoCs, incluindo capacidade real, custos e classificação de laboratórios por nível de risco.

## 8. Regras de negócio

- **BR-001:** somente laboratórios publicados e atribuídos podem ser iniciados por alunos.
- **BR-002:** sessão, tentativa e resultado sempre apontam para versão imutável do laboratório.
- **BR-003:** acesso ao gateway exige token de curta duração vinculado a usuário, sessão e finalidade.
- **BR-004:** sessão expirada não pode receber novas submissões nem comandos de terminal.
- **BR-005:** reset nunca apaga histórico acadêmico; novas tentativas recebem IDs próprios.
- **BR-006:** resultado válido exige avaliação originada no serviço confiável, não em retorno do contêiner do aluno.
- **BR-007:** pontuação e critérios de conclusão são versionados; mudanças não reprocessam resultados antigos automaticamente.
- **BR-008:** todas as operações administrativas críticas são auditadas.
- **BR-009:** ausência de rede externa é o padrão; exceções exigem aprovação e manifesto explícito.
- **BR-010:** falhas de limpeza e avaliação não podem levar a aprovação acadêmica por padrão (*fail closed*).
- **BR-011:** prazo de retenção de código, logs e resultados precisa ser definido por classificação de dado antes do piloto.
- **BR-012:** nenhuma imagem de laboratório contém dados reais, segredos de produção ou tokens do plano de controle.

## 9. Cenários excepcionais obrigatórios

| Cenário | Comportamento esperado |
|---|---|
| Provisionamento falha por quota | Sessão recebe estado de erro explicável, sem recursos órfãos |
| Aluno fecha navegador | Sessão permanece até TTL/política, sem liberar acesso indevido |
| Aluno recarrega durante provisionamento | Mesmo session_id, sem duplicar workloads |
| WebSocket perde conexão | Reconexão autenticada e autorizada se sessão válida |
| Sessão expira durante avaliação | Política consistente e atômica para concluir ou cancelar tentativa; sem nota falsa |
| Aluno tenta acessar URL de colega | 403/404 sem vazamento de metadados |
| Aluno altera resultados locais | Runner não confia em arquivos ou logs editáveis |
| Avaliação excede timeout | Estado de falha explícito; nenhuma aprovação |
| Worker para após criar contêiner | Reconciliador detecta e decide recuperar ou limpar |
| Sandbox tenta rede interna / metadados | Bloqueio de acesso e evento de segurança |
| Administrador aposenta versão | Sessões existentes seguem política documentada; início novo bloqueado |

## 10. Contratos e APIs: superfície preliminar

> Rotas propostas, não implementadas. A especificação OpenAPI ficará em `13_API_SPEC.md`.

| Método | Rota | Responsabilidade |
|---|---|---|
| GET | `/api/v1/laboratories` | Listar labs autorizados |
| GET | `/api/v1/laboratories/{id}` | Detalhes/versão publicada |
| POST | `/api/v1/sessions` | Criar sessão idempotente |
| GET | `/api/v1/sessions/{id}` | Consultar estado e endpoints autorizados |
| POST | `/api/v1/sessions/{id}/reset` | Reset controlado |
| POST | `/api/v1/sessions/{id}/terminate` | Encerrar sessão |
| POST | `/api/v1/sessions/{id}/attempts` | Criar tentativa e avaliação |
| GET | `/api/v1/attempts/{id}` | Consultar progresso e feedback |
| GET | `/api/v1/me/progress` | Histórico acadêmico próprio |
| GET | `/api/v1/instructor/cohorts/{id}/results` | Relatório por turma |
| GET | `/api/v1/instructor/cohorts/{id}/results.csv` | Exportação autorizada |
| GET | `/api/v1/admin/sessions` | Visão operacional (admin) |

Requisitos transversais: autorização por recurso, limite de taxa, validação de entrada, IDs não sequenciais, idempotency-key, paginação, correlation_id, versionamento e error codes consistentes.

## 11. Modelo de dados conceitual

Entidades iniciais: `User`, `RoleAssignment`, `Cohort`, `CohortMembership`, `Laboratory`, `LaboratoryVersion`, `LabAssignment`, `Session`, `RuntimeInstance`, `Attempt`, `EvaluationRun`, `CriterionResult`, `Completion`, `AuditEvent` e `PublishedArtifact`.

Relações centrais:

- Um `Laboratory` possui muitas `LaboratoryVersion`.
- Uma `LabAssignment` autoriza um `User` ou `Cohort` a executar versão elegível.
- Uma `Session` pertence a um `User` e referencia uma `LaboratoryVersion`.
- Uma `Session` possui zero ou mais `Attempt`; cada `Attempt` possui `EvaluationRun` e `CriterionResult`.
- `Completion` consolida progresso e não depende da existência de `RuntimeInstance`.
- `AuditEvent` guarda ator, evento, correlação e contexto mínimo, sem segredos.

O desenho lógico/físico, chaves, índices, retenção e transações pertencem a `12_DATA_MODEL.md`.

## 12. Quatro laboratórios e objetivos de avaliação

### LAB-001 SQL Injection

- **Stack:** Python Flask + SQLite.
- **Tarefa:** demonstrar acesso indevido em dataset sintético e corrigir consulta para usar parâmetros.
- **Validação:** prova funcional de exploração, rejeição de payloads e preservação da consulta legítima.
- **Teste do motor:** persistência de arquivos, app web, banco e testes de regressão.

### LAB-002 Broken Access Control / IDOR

- **Stack:** Python Flask + REST.
- **Tarefa:** acessar indevidamente recurso sintético de outro usuário e implementar autorização no servidor.
- **Validação:** identidade A não acessa dados de B, enquanto acesso legítimo continua funcional.
- **Teste do motor:** múltiplas identidades sintéticas e evidência de acesso por recurso.

### LAB-003 JWT Authentication Security

- **Stack:** Node.js + REST.
- **Tarefa:** identificar erro de verificação de token e aplicar configuração/validação segura.
- **Validação:** tokens de teste inválidos rejeitados; tokens legítimos aceitos.
- **Teste do motor:** segundo runtime, suites de testes parametrizadas.

### LAB-004 OS Command Injection

- **Stack:** Flask + Linux com isolamento reforçado aprovado.
- **Tarefa:** demonstrar efeito local e controlado de comando indevido e remover a injeção.
- **Validação:** requisição manipulada não executa processo arbitrário; função esperada continua funcionando.
- **Teste do motor:** endurecimento de sandbox, recursos/processos e proibição de egress.
- **Gate:** não publicar sem relatório de contenção aprovado; substituir lab se sandbox não atender requisitos.

Todos os datasets, usuários, tokens e segredos de exercício são sintéticos e efêmeros. A política de dicas, pontuação e número máximo de tentativas será refinada por laboratório antes da homologação.

## 13. Requisitos de segurança por fronteira de confiança

1. **Navegador → API:** OIDC, CSRF conforme modelo de sessão, validação de JWT/cookies, autorização em toda operação e rate limiting.
2. **API → orquestrador:** credenciais de serviço limitadas, policy-as-code e limites de namespace/runtime.
3. **Navegador → gateway → sandbox:** sessões temporárias, rota restrita à instância do aluno, anti-SSRF, WebSocket autenticado.
4. **Sandbox → rede:** negar por padrão conexões externas, rede interna e endpoints cloud metadata; somente allowlists justificadas.
5. **Sandbox → runner:** nunca dar ao sandbox acesso aos validadores; runner aceita dados não confiáveis em contexto de execução restrito.
6. **Runner → resultados:** mensagens autenticadas, integridade e escrita autorizada somente pelo serviço de controle.
7. **CI/CD → registry:** publicação controlada, imagens imutáveis, varredura e rastreabilidade.

Modelo de ameaças detalhado e testes em `07_THREAT_MODEL.md`; nenhum teste exploratório deve usar alvos externos.

## 14. Medição, telemetria e indicadores

### Produto / acadêmico

- Inscritos/atribuídos, sessões iniciadas e concluídas por laboratório.
- Tempo até primeira atividade e até conclusão; quantidade de tentativas.
- Taxa de aprovação, nota consolidada, consumo de dicas (se habilitado).
- Taxa de abandono e feedback da turma.

### Plataforma / operação

- `session_provision_duration_seconds` (p50/p95/p99) e taxa de falhas.
- Quantidade de sandboxes ativos por perfil e laboratório.
- `evaluation_duration_seconds`, erros por suíte, timeouts.
- TTL, sessões órfãs detectadas, tempo até cleanup.
- CPU/RAM e custo estimado por sessão, sem expor dados privados de alunos desnecessariamente.

Definir padrão de nomes e labels de observabilidade sem inserir PII desnecessária.

## 15. Critérios de aceite end-to-end (E2E)

**E2E-01:** aluno atribuído inicia LAB-001, workspace fica READY, edita arquivo, testa no navegador e submete; resultado permanece após encerrar sessão.

**E2E-02:** aluno não atribuído não inicia lab; aluno A não acessa nenhuma superfície de sessão de B por API, WebSocket ou gateway.

**E2E-03:** iniciar repetidamente com mesma chave produz uma sessão; retries após timeout são conciliados.

**E2E-04:** criar 30 sessões representativas cumpre metas de inicialização/provisionamento acordadas no ambiente piloto.

**E2E-05:** solução intencionalmente incorreta não passa; solução correta passa; alteração pós-snapshot não muda avaliação.

**E2E-06:** falha simulada do orquestrador não cria recursos persistentes órfãos; rotina de reconciliação limpa o ambiente.

**E2E-07:** sessão expirada perde acesso, mas relatório acadêmico mantém tentativas/nota.

**E2E-08:** pipeline publica nova versão de laboratório sem alteração em motor/API; resultados antigos mantêm referência imutável.

**E2E-09:** sandbox não acessa rede interna, metadata endpoints ou outro workspace; zero bloqueadores críticos após testes adversariais.

**E2E-10:** instrutor exporta resultados somente de sua turma, com campos e filtragem definidos.

## 16. Dependências e sequenciamento

1. Visão e requisitos aprovados → Threat model + PoCs.
2. PoC de isolamento → runtime/manifesto definitivo e limites de segurança.
3. Sessões idempotentes + sandbox → gateway/editor/terminal.
4. Snapshot consistente + runner → avaliação, feedback e persistência.
5. Publicação de laboratórios → integração dos quatro conteúdos.
6. Métricas, cleanup e testes adversariais → piloto.
7. Piloto e benchmark → decisão Go/No-Go e roadmap pós-MVP.

## 17. Definição de pronto (DoD) e gates

Todo item P0 exige: critérios de aceite implementados, testes automatizados relevantes, autorização/segurança revisadas, logs/métricas, documentação de contratos e rollback. O MVP exige, adicionalmente: evidência dos E2Es, teste de carga, revisão de isolamento e aprovação formal acadêmica/operacional/segurança.

**Bloqueadores automáticos:** falha crítica aberta de isolamento, exposição de segredos, validação forjável, acesso cruzado, perda de nota, incapacidade de limpar runtimes ou ausência de trilha de auditoria para operação crítica.

## 18. Backlog e controle de mudanças

Épicos sementes em `15_PRODUCT_BACKLOG.md`: identidade, catálogo, sessão, provisionamento, workspace, avaliação, progresso, conteúdo, segurança, operação, relatórios, integração e pipeline. Cada história deverá referenciar `FR`/`NFR`, risco, dependências, testes e responsável. Mudanças P0 precisam de aprovação do PO e avaliação de impacto técnico e de segurança.

## 19. Pendências para refinamento (não presumir respostas)

| ID | Decisão pendente | Responsável sugerido | Prazo lógico |
|---|---|---|---|
| OPEN-01 | Provedor OIDC e política de sessão | Produto / arquitetura | Antes de FR-001 |
| OPEN-02 | Host/cloud e runtime de isolamento | Plataforma / segurança | Antes do motor |
| OPEN-03 | TTL, retomada e política de reset | Produto / operações | Antes de FR-024 |
| OPEN-04 | Modelo de nota e tentativas | Acadêmico / produto | Antes do validador final |
| OPEN-05 | Retenção LGPD por tipo de dado | Jurídico / segurança | Antes do piloto |
| OPEN-06 | Campos do dashboard e CSV | Instrutores / produto | Antes de FR-050 |
| OPEN-07 | Orçamento por sessão e limites | Operações / produto | Antes do teste de carga |
| OPEN-08 | Necessidade de segregação por cliente no piloto | Produto / comercial | Antes do modelo de turmas |
| OPEN-09 | Política de acesso à internet em labs | Segurança / arquitetura | Antes do manifesto final |
| OPEN-10 | Escopo mínimo da API para Moodle | Acadêmico / arquitetura | Após P0 estável |

## 20. Aprovação e rastreabilidade

**Status atual:** rascunho, não aprovado.

| Disciplina | Aprovação | Data |
|---|---|---|
| Produto / PO | Pendente |  |
| Arquitetura | Pendente |  |
| Segurança | Pendente |  |
| Operação / SRE | Pendente |  |
| Acadêmico | Pendente |  |

Referências internas: `00_PRODUCT_VISION.md`, `06_SYSTEM_ARCHITECTURE.md`, `07_THREAT_MODEL.md`, `08_LAB_ENGINE_SPEC.md`, `10_VALIDATION_ENGINE_SPEC.md`, `11_LAB_MANIFEST_SPEC.md`, `14_MVP_SCOPE.md`, `15_PRODUCT_BACKLOG.md`.

## 15. Complemento aprovado para detalhamento: experiência didática e hospedagem (v0.3)

A partir dos comentários do Product Owner, o MVP deve possuir experiência **pedagógica por etapas**, e não apenas execução/avaliação ao fim da sessão. Requisitos adicionais: `LEX-001` storytelling (contexto, CWE e aplicação-alvo); `LEX-002` uma vulnerabilidade central por lab; `LEX-003` explicação e conceito por passo; `LEX-004` código realista e ações de build/execução por runtime; `LEX-005` validação automática por passo, desbloqueio sequencial e dicas progressivas; `LEX-006` variantes de linguagem compartilhando objetivos e narrativa. Consultar `21_LEARNING_EXPERIENCE_SPEC.md` para critérios e exemplos.

**Hospedagem inicial definida:** on-premises. As decisões de orquestrador e sandbox continuam condicionadas às PoCs, conforme `ADR/ADR-004-on-premises-hosting.md`.

**Ressalva de escopo:** suporte a variantes é obrigatório no schema e APIs do MVP; produzir duas ou mais implementações do mesmo lab não é obrigatório para os quatro labs iniciais. Incluir teste de contrato com variantes simuladas ou homologação separada. O desbloqueio de etapas ocorre exclusivamente após avaliação confiável persistida, com controle transacional.
