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

**A desenvolver.** Referenciar FR/NFR, evidências e ADRs aplicáveis. Não assumir tecnologia ou requisito não aprovado.

### 3. LAB-003 JWT: Node.js/REST

**A desenvolver.** Referenciar FR/NFR, evidências e ADRs aplicáveis. Não assumir tecnologia ou requisito não aprovado.

### 4. LAB-004 OS Command Injection: Flask/Linux isolado

**A desenvolver.** Referenciar FR/NFR, evidências e ADRs aplicáveis. Não assumir tecnologia ou requisito não aprovado.

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
