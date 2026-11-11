# 00. Visão do Produto | CECyber AppSec Labs

| Campo | Valor |
|---|---|
| Produto (nome definido) | CECyber AppSec Labs |
| Documento | Visão do Produto |
| Versão | 0.1.0 |
| Estado | Proposta para validação |
| Data | 2026-11-11 |
| Patrocinador / Product Owner | A definir formalmente |
| Horizonte inicial | MVP com 4 laboratórios e piloto controlado |

## 1. Resumo executivo

Construir uma plataforma própria de laboratórios práticos de cibersegurança que permita a alunos **executar, explorar e corrigir** aplicações deliberadamente vulneráveis diretamente no navegador. A plataforma oferecerá criação de sessões isoladas sob demanda, ambiente de edição/terminal/aplicação, verificação automática de exercícios e rastreamento acadêmico. A capacidade central do produto será um **motor genérico** com manifestos versionados, provisionamento, avaliação confiável e ciclo de vida independente do conteúdo.

O objetivo do MVP não é competir em abrangência com plataformas comerciais, e sim comprovar um fluxo completo, seguro, reprodutível e suficientemente extensível para expansão do catálogo.

## 2. Problema e oportunidade

Programas de AppSec e Security Champions precisam de prática frequente, mensurável e alinhada à realidade de desenvolvimento. Laboratórios montados manualmente demandam suporte, geram divergências entre máquinas e dificultam a medição do aprendizado. Soluções de execução ad hoc tendem a acoplar conteúdo, infraestrutura e avaliação, tornando difícil criar novos desafios.

**Oportunidade:** unificar experiência pedagógica e operação técnica, reduzindo tempo de preparação e permitindo que autores publiquem laboratórios padronizados sem alterar o motor.

## 3. Declaração de visão

> Para alunos, instrutores e equipes de capacitação que precisam desenvolver competências práticas em segurança de software, o CECyber AppSec Labs será uma plataforma de laboratórios isolados e avaliados automaticamente. Diferentemente de exercícios manuais ou ambientes descartáveis sem acompanhamento, oferecerá um motor reutilizável de execução, avaliação, observabilidade e progressão acadêmica, preparado para integração com a CECyber Academy.

## 4. Públicos e jobs to be done

| Público | Necessidade principal | Resultado esperado |
|---|---|---|
| Aluno | Praticar vulnerabilidades sem configurar máquina local | Iniciar, executar, corrigir e receber retorno claro |
| Instrutor / gestor | Acompanhar desempenho de uma turma | Consultar progresso, tentativas e exportar resultados |
| Autor de laboratórios | Publicar novo exercício sem mudar a plataforma | Empacotar conteúdo, runtime e verificações versionadas |
| Operador / administrador | Operar ambientes com previsibilidade | Ver sessões, falhas, consumo, expiração e auditoria |
| Time acadêmico | Incorporar prática a cursos e trilhas | Integrar resultados com LMS em evolução posterior |

## 5. Proposta de valor

1. **Prática sem instalação local:** editor, terminal e aplicação via navegador.
2. **Ambiente exclusivo por sessão:** um aluno não interfere no outro.
3. **Feedback com evidência:** validação de exploração, correção e regressão.
4. **Conteúdo independente do motor:** manifesto, imagem e validadores versionados.
5. **Operação sob demanda:** limites, expiração, limpeza e métricas.
6. **Evolução modular:** novos runtimes, laboratórios, turmas e integrações sem reconstrução do núcleo.

## 6. Objetivos e resultados-chave propostos

| Objetivo | Medida de aceite inicial | Observações |
|---|---|---|
| Demonstrar experiência de ponta a ponta | 4 laboratórios executáveis do navegador | Cada um com exploração e correção |
| Testar a extensibilidade | Publicar laboratório/versão sem alterar código do motor | Evidência em pipeline e manifesto |
| Garantir isolamento mínimo seguro | Zero falhas críticas conhecidas em testes adversariais | Gate obrigatório para piloto |
| Sustentar piloto | 30 sessões simultâneas em teste controlado | Meta provisória; dimensionar por benchmark |
| Disponibilização | >=98% de provisionamentos válidos bem-sucedidos | Definir janela, amostra e exclusões no plano de teste |
| Tempo de inicialização | P95 <=60 s nos laboratórios simples | Medir da solicitação à sessão READY |
| Provar avaliação confiável | Testes repetíveis para soluções corretas e incorretas | Incluir tentativas de manipulação |
| Gerar evidências acadêmicas | Histórico por aluno, laboratório, versão, tentativa | Exportação CSV e API prevista |

As metas são **hipóteses de planejamento**, não SLAs assumidos ou resultados já medidos.

## 7. Escopo do MVP

### Incluído (P0)

- Login OIDC e RBAC essencial: aluno, instrutor, administrador; autorização de proprietário da sessão.
- Catálogo interno de quatro laboratórios versionados, com manifesto validado.
- Provisionamento sob demanda de sandbox exclusivo por aluno, com quotas, TTL, expiração e limpeza.
- Interface de instruções, editor, terminal e acesso autenticado à aplicação web.
- Avaliação automatizada em runner confiável isolado do workspace; feedback, pontuação, histórico de tentativas.
- Dashboard operacional básico e visibilidade de progresso para instrutores; exportação CSV.
- Logs e métricas mínimas, alertas de falha crítica, esteira de publicação de laboratórios.
- Testes adversariais de isolamento e validação antes de qualquer piloto com usuários reais.

### Preparado na arquitetura, mas fora da entrega P0

- LTI 1.3 com Moodle e retorno de notas; API de resultados poderá ser incluída se não impactar gates críticos.
- Editor visual/no-code, gamificação avançada, marketplace, multi-tenancy empresarial completo.
- Runtimes de Windows/AD, infraestrutura multicloud e ambientes colaborativos.
- Tutoria IA, geração automática de desafios e cobrança.

### Quatro laboratórios iniciais

| ID | Tema | Runtime inicial | Diferencial para o motor |
|---|---|---|---|
| LAB-001 | SQL Injection | Flask + SQLite | Banco, edição de código e regressão |
| LAB-002 | Broken Access Control / IDOR | Flask + REST | Identidades e autorização por recurso |
| LAB-003 | JWT Authentication Security | Node.js + REST | Segundo runtime, tokens e testes de autenticidade |
| LAB-004 | OS Command Injection | Flask + Linux isolado | Execução de processo e requisitos mais severos de isolamento |

O LAB-004 fica condicionado ao aceite formal de controles de contenção; se não aprovado, será substituído por um exercício com risco operacional menor.

## 8. Princípios de arquitetura e produto

- **Separação de confiança:** controle, execução e avaliação são domínios isolados.
- **Zero confiança em código do aluno:** arquivos, logs e scripts no workspace podem ser manipulados.
- **Isolamento comprovado:** a tecnologia de sandbox deve ser escolhida em PoC; contêiner comum não é automaticamente fronteira adequada.
- **Especificação declarativa e versionada:** manifestos e contratos evoluem por esquema.
- **Idempotência e recuperação:** operações repetidas não criam recursos duplicados.
- **Menor privilégio e rede bloqueada por padrão:** sem acesso a control plane, host ou redes internas.
- **Portabilidade:** abstrair runtime via interface de provisionamento.
- **Academic progress ≠ runtime state:** notas sobrevivem a reset, expiração e destruição da sessão.
- **Observabilidade nativa:** métricas e correlação de eventos desde a primeira versão.
- **Simplicidade consciente:** monólito modular de controle é preferível a uma malha prematura de microsserviços.

## 9. Jornada principal de valor

1. Usuário autenticado identifica laboratório publicado e autorizado.
2. Plataforma cria sessão e enfileira provisionamento.
3. Sandbox exclusivo torna-se READY; gateway libera acesso temporário.
4. Aluno lê instruções, explora a falha e altera código.
5. Aluno solicita avaliação; runner confiável executa verificações contra uma revisão consistente do workspace.
6. Plataforma registra resultado/feedback e permite nova tentativa conforme política.
7. Ao concluir ou expirar, o ambiente é desativado e limpo; histórico acadêmico permanece.
8. Instrutor acompanha evolução por participante e laboratório.

## 10. Modelo de negócio / adoção: hipóteses

O primeiro caso de uso é o suporte a programas de capacitação da CECyber. Uma possível evolução B2B inclui gestão por organização, turmas, controle de consumo e relatórios por cliente. Não assumir recursos comerciais ou multi-tenant no MVP antes da validação dos requisitos e custos.

## 11. Limites e premissas

- Ambientes de laboratório são exclusivamente de treinamento autorizado e sem alvos externos.
- Não são permitidos dados reais de clientes, segredos corporativos ou credenciais de produção.
- Conteúdo e interfaces serão inicialmente em pt-BR; internacionalização não bloqueia MVP.
- Piloto terá usuários convidados e capacidade limitada.
- Escolhas de cluster, sandbox e custo devem ser validadas em PoCs; o plano de 16 semanas é apenas estimativa condicional.
- O nome oficial definido é `CECyber AppSec Labs`.

## 12. Riscos estratégicos

| Risco | Efeito | Resposta planejada |
|---|---|---|
| Sandbox insuficiente | Comprometimento entre sessões ou do host | Threat model, PoC, egress deny, testes adversariais e gate Go/No-Go |
| Validação manipulável | Pontuação sem competência real | Runner isolado, testes ocultos, replay adversarial |
| Plataforma muito acoplada ao catálogo | Custo crescente por lab | Manifesto, contratos, pipeline e teste de novo laboratório |
| Custos por usuário não previstos | Ineficiência do modelo | Quotas, TTL, métricas e benchmark de concorrência |
| Escopo excessivo | Atraso e complexidade | P0/P1/P2 com gates e controle de mudança |

## 13. Critérios para declarar o MVP concluído

1. Todos os quatro labs passam pela mesma API e motor de sessão.
2. Provisionamento, editor, terminal, web app, validação e limpeza funcionam de ponta a ponta.
3. Históricos são consistentes diante de falhas, reset e expiração.
4. Testes adversariais não revelam falhas críticas abertas de isolamento, autorização ou avaliação.
5. O teste controlado com 30 sessões simultâneas atende às metas acordadas.
6. Uma nova versão de laboratório pode ser publicada por pipeline, sem alterar o motor.
7. Operação dispõe de métricas, troubleshooting e procedimento de rollback.
8. Piloto com alunos e instrutores recebe aceite formal baseado nas evidências.

## 14. Governança de decisões e próximos documentos

1. Aprovar esta visão com produto, arquitetura, operação e equipe acadêmica.
2. Refinar `02_PRD.md`, transformando requisitos em histórias e testes.
3. Completar `07_THREAT_MODEL.md` e os ADRs de isolamento, runtime e avaliação.
4. Executar PoCs antes da implementação de fluxos completos e da abertura a usuários.
5. Refinar `15_PRODUCT_BACKLOG.md` com dependências, estimativas da equipe e responsáveis.

## 15. Questões em aberto

- Quem será o Product Owner e quem fará aceites acadêmicos e de segurança?
- Qual provedor de identidade OIDC atenderá o piloto?
- A hospedagem inicial é on-premises; especificar recursos de hardware, virtualização, rede, segurança e orçamento disponíveis.
- Qual orçamento de infraestrutura e limite de custo por sessão?
- Qual runtime isolado será aprovado pela equipe de segurança?
- Quanto tempo será permitido pausar, reiniciar e retomar o workspace?
- Precisaremos de segregação por cliente já no primeiro piloto, ou somente por turma?
- Quais métricas acadêmicas devem compor o primeiro dashboard?

**Documentos relacionados:** `02_PRD.md`, `06_SYSTEM_ARCHITECTURE.md`, `07_THREAT_MODEL.md`, `14_MVP_SCOPE.md`, `15_PRODUCT_BACKLOG.md`.

## Atualização v0.3: nome, implantação e experiência didática

Nome oficial: **CECyber AppSec Labs**. Implantação inicial definida para **on-premises**. Os laboratórios devem conter storytelling com CWE e aplicação realista, uma vulnerabilidade central, sequência de passos com explicações, editor/terminal/build/run, validação e desbloqueio por etapa, dicas graduais e suporte arquitetural a variantes de linguagem. Ver `21_LEARNING_EXPERIENCE_SPEC.md` e `ADR/ADR-004-on-premises-hosting.md`.
