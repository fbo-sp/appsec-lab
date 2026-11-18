# 17. Catálogo dos Quatro Laboratórios

| Campo | Valor |
|---|---|
| Versão | 0.1.0 |
| Estado | Estrutura inicial, **não é especificação aprovada** |
| Data | 2026-11-11 |
| Fontes | `00_PRODUCT_VISION.md`, `02_PRD.md` |

## Propósito

Detalhar **catálogo dos quatro laboratórios** com rastreabilidade aos requisitos, testes e decisões. Este arquivo é um ponto de partida para trabalho incremental com Codex/Claude Code; itens sem decisão registrada devem continuar como **pendentes**.

## Seções para desenvolvimento

### 1. LAB-001 SQL Injection: Flask/SQLite

**Implementado, só local** (2026-11-13). Proposta e decisões aprovadas pelo PO em 2026-11-13. Requisitos: PRD §12, US-022, LEX-001–005, IMP-501. ADRs: 005, 006, 008, 010 e 012.

- **Cenário.** O aluno é desenvolvedor(a) da Clínica VidaPlena (fictícia). A busca "Encontre um médico" do portal de agendamento expõe as tabelas `pacientes` e `configuracoes`. Os dados são 100% fictícios: CPFs com dígito inválido e e-mails em domínio `.example`.
- **Aplicação** (`laboratories/LAB-001-sqli-clinica/runtime/workspace`). Flask com camadas controller, serviço, repositório, modelo e template, e identificadores em português (decisão do PO). A falha está em `MedicoRepository.buscar_por_nome`, que monta o SQL com f-string. O banco e o log ficam em `/tmp`, e o banco é recriado a cada início. A aplicação recarrega ao salvar e roda sem o depurador interativo.
- **Recursos.** 0,5 vCPU, 512 MiB, 256 MiB de disco e 64 PIDs. Prazo de 45 min com até 2 renovações. Sem egress.
- **Etapas** (100 pontos, desbloqueio sequencial, 3 dicas por etapa):

| # | Etapa | Validação | Pts |
|---|---|---|---|
| 1 | Conhecer a aplicação | Resposta `buscar_por_nome` (`sqli/answer/locate-query-v1`) | 10 |
| 2 | Provocar um erro | Resposta `OperationalError`, lida em `/tmp/app.log` (`sqli/answer/error-type-v1`) | 15 |
| 3 | Medir a consulta | Resposta `4` via `ORDER BY` (`sqli/answer/column-count-v1`) | 15 |
| 4 | Extrair dados sensíveis | Token fictício lido com `UNION` (`sqli/answer/integration-token-v1`) | 20 |
| 5 | Corrigir com consulta parametrizada | Suíte comportamental com 7 verificações em cópia isolada (`sqli/python-flask/parameterized-search-v1`) | 40 |

- **Suíte da correção.** Verifica:
  - busca parcial;
  - busca vazia;
  - nome com apóstrofo (D'Ávila);
  - aspa sem erro 500;
  - `UNION` contra `pacientes` e contra `configuracoes`;
  - condição `OR '1'='1' --`.

  Com Docker real (`tests/test_lab001_validation.py`), o código original e as "correções" que removem ou bloqueiam aspas reprovam. As correções com `?` e com parâmetro nomeado passam. Escapar aspas duplicando-as também passa, e isso é aceito por ser seguro no SQLite.
- **Limitações aceitas pelo PO para o MVP local:**
  - as respostas das etapas 2 a 4 são fixas e podem ser repassadas entre alunos;
  - o banco pode ser lido pelo terminal, porque terminal e aplicação usam o mesmo usuário.

  A correção (40 pts) é sempre validada pelo comportamento.
- **Para ir além** (resumo final): erros genéricos, limite de entrada, menor privilégio no banco, SQL cru em ORMs e segredos fora do código.

### 2. LAB-002 IDOR: Flask/REST

**Implementado para teste do PO, só local** (2026-11-13). O cenário foi escolhido pelo PO em card de decisão. Requisitos: US-023, LEX-001–005, IMP-502. ADRs: 008, 010, 012, 013 e 015.

- **Cenário.** O aluno é desenvolvedor(a) do Banco Vértice Digital (fictício). Em "Meus comprovantes de PIX", trocar o número na URL ou na API (`/api/comprovantes/<n>`) mostra o comprovante de outro cliente. Documentos aparecem mascarados e os domínios são `.example`.
- **Aplicação** (`laboratories/LAB-002-idor-banco`). Flask com login por sessão e camadas controller, serviço, repositório e modelo. A falha está em `ComprovanteService.obter`, que recebe o `cliente_id` da sessão mas busca só pelo número. O banco SQLite fica em `/tmp` e é recriado a cada início.
- **Recursos.** Os mesmos do LAB-001.
- **Etapas** (100 pontos, 3 dicas por etapa):

| # | Etapa | Validação | Pts |
|---|---|---|---|
| 1 | Conhecer a aplicação | `buscar_por_id` (`idor/answer/locate-lookup-v1`) | 10 |
| 2 | Observar o identificador | `10458`, o comprovante mais recente (`idor/answer/latest-receipt-v1`) | 15 |
| 3 | Abrir o comprovante de outro cliente | `Rodrigo Tavares Lima` (`idor/answer/other-payer-v1`) | 15 |
| 4 | Medir o impacto | `34` comprovantes alheios lidos com `curl` em laço (`idor/answer/leaked-count-v1`) | 20 |
| 5 | Corrigir verificando o dono | Suíte com 8 verificações e 2 clientes autenticados (`idor/python-flask/owner-check-v1`) | 40 |

- **Suíte da correção.** Verifica:
  - a dona continua vendo o próprio comprovante na página, na API e na lista;
  - outro cliente não aparece na página nem na API, que responde 404 ou 403;
  - `?cliente_id=` forjado não libera o comprovante;
  - o dono legítimo continua vendo o seu;
  - sem login, nada é entregue.

  Com Docker real (`tests/test_lab002_validation.py`), estas versões reprovam: o código original, a que protege só a página HTML, a que confia em `?cliente_id=` e a que bloqueia todo mundo.

### 3. LAB-003 JWT: Node.js/REST

**Implementado para teste do PO, só local** (2026-11-13). O cenário foi escolhido pelo PO em card de decisão. Requisitos: US-024, LEX-001–005, IMP-503. ADRs: 008, 010, 012, 013 e 015.

- **Cenário.** O aluno é desenvolvedor(a) da API do Portal Orbe, uma emissora de cartões fictícia. O middleware lê o JWT com `jwt.decode`, sem verificar a assinatura. Com um token forjado (`alg: none`, perfil `admin`), a cliente entra no painel do gerente e aumenta o próprio limite.
- **Aplicação** (`laboratories/LAB-003-jwt-cartoes`). Node.js 22 com Express 4.21 e jsonwebtoken 9 (dependências em `/opt/lab`, fora do workspace). Camadas de rotas, middlewares, controllers, serviços e repositórios em memória. A interface web é estática. Recarrega com `node --watch`. Usa a imagem base `base-node`, derivada da base Python com o mesmo agente de workspace.
- **Etapas** (100 pontos, 3 dicas por etapa):

| # | Etapa | Validação | Pts |
|---|---|---|---|
| 1 | Conhecer a aplicação | `lerToken` (`jwt/answer/locate-reader-v1`) | 10 |
| 2 | Ler o conteúdo do token | `cliente` (`jwt/answer/profile-claim-v1`) | 15 |
| 3 | Forjar um token de gerente | `ORB-AUD-5583-QX` (`jwt/answer/audit-code-v1`) | 15 |
| 4 | Medir o impacto | `ORB-LIM-4821-50000` (`jwt/answer/limit-protocol-v1`) | 20 |
| 5 | Corrigir verificando a assinatura | Suíte com 8 verificações e logins de cliente e gerente (`jwt/node-express/verify-signature-v1`) | 40 |

- **Suíte da correção.** Verifica:
  - cliente e gerente legítimos continuam funcionando;
  - a cliente continua sem acesso ao painel (403);
  - são recusados os tokens `alg: none`, os assinados com outra chave, os adulterados (perfil trocado com a assinatura original) e os expirados;
  - não é possível alterar limite com token forjado.

  Com Docker real (`tests/test_lab003_validation.py`), estas versões reprovam: o código original, a que só barra `alg: none`, a que usa `ignoreExpiration` e a que barra todo `admin`. Erro de sintaxe é informado como "aplicação não iniciou".

### 4. LAB-004 OS Command Injection: Flask/Linux isolado

**Implementado para teste do PO, só local** (2026-11-13). O cenário foi escolhido pelo PO em card de decisão. Requisitos: US-025, LEX-001–005, IMP-504. ADRs: 002, 008, 010, 012, 013 e 015. **G5 (contenção validada) é obrigatório antes de qualquer ambiente além do local.**

- **Cenário.** O aluno é desenvolvedor(a) do Portal de Manutenção da Ferrara Metais, Planta Contagem (fictícia). O teste de comunicação com CLPs monta `diag-clp {endereco}` e executa com `shell=True`. Os CLPs são simulados e o `scada.conf` é fictício.
- **Contenção.** A injeção roda dentro do contêiner da sessão, com:
  - o usuário 10001, sem capabilities e com `no-new-privileges`;
  - limite de PIDs e sem egress.

  O alcance é o mesmo do terminal do aluno (ver ADR-015).
- **Etapas** (100 pontos, 3 dicas por etapa):

| # | Etapa | Validação | Pts |
|---|---|---|---|
| 1 | Conhecer a aplicação | `diag-clp` (`cmdi/answer/locate-program-v1`) | 10 |
| 2 | Encadear um comando | `lab`, saída de `; whoami` (`cmdi/answer/process-user-v1`) | 15 |
| 3 | Explorar o servidor | `scada.conf` (`cmdi/answer/scada-file-v1`) | 15 |
| 4 | Medir o impacto | `SCADA-OPR-4471-KX` (`cmdi/answer/scada-password-v1`) | 20 |
| 5 | Corrigir sem shell e com validação | Suíte com 9 verificações (`cmdi/python-flask/no-shell-v1`) | 40 |

- **Suíte da correção.** Verifica:
  - um CLP cadastrado e um endereço sem resposta continuam sendo testados;
  - `;`, `&&`, `|`, `||`, `$( )`, crases e quebra de linha não executam comandos. A suíte usa um marcador que só aparece se o shell executar o comando.

  Com Docker real (`tests/test_lab004_validation.py`), passam três correções: a documentada (`ipaddress` mais lista de argumentos), só lista de argumentos e `shlex.quote`. Reprovam o código original e as listas de bloqueio.

### 5. Objetivos, etapas, dicas e pontuação

**A desenvolver.** Referenciar FR/NFR, evidências e ADRs aplicáveis. Não assumir tecnologia ou requisito não aprovado.

### 6. Critérios de testes positivos, negativos e regressão

**A desenvolver.** Referenciar FR/NFR, evidências e ADRs aplicáveis. Não assumir tecnologia ou requisito não aprovado.

### 7. Política de publicação e segurança

**A desenvolver.** Referenciar FR/NFR, evidências e ADRs aplicáveis. Não assumir tecnologia ou requisito não aprovado.

## Critérios para sair de rascunho

- [ ] Conteúdo elaborado e revisado por responsável técnico/negócio.
- [ ] Rastreabilidade com FR/NFR e backlog.
- [ ] Casos de erro, segurança e testes especificados.
- [ ] Decisões abertas registradas em ADR ou registro de riscos.
- [ ] Aprovação formal registrada.

## Adendo v0.3: padrão editorial obrigatório

Cada um dos quatro laboratórios precisa ter: cenário realista fictício, papel do aluno, CWE principal, aplicação-alvo, somente uma vulnerabilidade central, etapas com explicações, conceito, tarefa e verificador; dicas graduais; código editável com estrutura plausível; operação build/run aplicável e verificação automática com desbloqueio sequencial. Variantes de linguagem opcionais no conteúdo do MVP, obrigatórias no modelo. Ver `21_LEARNING_EXPERIENCE_SPEC.md`.
