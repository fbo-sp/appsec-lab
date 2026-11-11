# 14. Escopo Controlado do MVP

| Campo | Valor |
|---|---|
| Produto | CECyber AppSec Labs |
| Versão | 0.3.0 |
| Estado | Proposta de baseline do MVP |
| Hospedagem | On-premises, sujeita a inventário e PoC |
| Escala de teste | Meta proposta: 30 sessões simultâneas |

## 1. Resultado esperado

Quatro laboratórios com **uma vulnerabilidade-alvo por laboratório**, narrativa contextualizada, CWE principal, aplicação realista, etapas sequenciais com conceito/instrução, dicas graduais, editor, terminal, ações de build/interpretador conforme runtime e **validação automática que libera a etapa seguinte**. A arquitetura suporta múltiplas linguagens no mesmo laboratório conceitual, embora o MVP possa entregar uma variante por lab.

## 2. Obrigatório P0

- Login OIDC; RBAC e ownership de recursos, sessões e WebSockets.
- Catálogo versionado, storytelling, CWE, aplicação de exemplo e objetivos.
- Manifestos declarativos, variantes de linguagem e release imutável.
- Interface web com instrução por etapa, conceito, dicas, progresso e bloqueio de passos posteriores.
- Editor de código, terminal, preview web e compilação/interpretação por comandos controlados.
- Sessão efêmera individual com TTL, reset, encerramento, reconciliação e auditoria.
- Sandbox on-premises com isolamento comprovado, egress restrito e limites de recursos.
- Validador separado do workspace com testes positivos, negativos e de regressão; feedback e pontuação auditáveis.
- Dashboard mínimo por turma, exportação CSV, logs e métricas de operações.
- Pipeline para um autor técnico publicar labs sem alterar o motor.

## 3. Quatro laboratórios

| ID | Vulnerabilidade única | CWE principal | Variante inicial proposta | Relevância técnica |
|---|---|---|---|---|
| LAB-001 | SQL Injection | CWE-89 | Python/Flask | Web + banco + edição e interpretação |
| LAB-002 | IDOR / autorização horizontal | CWE-639 | Python/Flask | Usuários de teste e autorização |
| LAB-003 | Validação inadequada de JWT | CWE-347 | Node.js | Segundo runtime e validação de tokens |
| LAB-004 | OS Command Injection | CWE-78 | Python/Flask | Contenção de execução de processos |

LAB-004 só será liberado após PoC e teste adversarial de sandbox. Se não houver isolamento adequado, substituí-lo por outra vulnerabilidade de menor risco, mantendo quatro laboratórios.

## 4. Fora do MVP (P2)

Editor no-code de conteúdo, marketplace, CTF competitivo, geração IA de soluções, correção por IA, execução de ataques externos, AD/Windows, multi-tenancy B2B completo, provisionamento de contas cloud, integração Moodle LTI 1.3 com AGS e gamificação avançada. **Não confundir suporte a variantes no motor com obrigação de publicar várias variantes no MVP.**

## 5. Gates

1. **G1 Requisitos:** visão, PRD e critérios de aceitação validados.
2. **G2 PoC infraestrutura:** host on-prem, hipervisor/runtime, rede de sandbox, DNS/certificados, storage e backup definidos; sem caminho do sandbox para rede administrativa.
3. **G3 Motor:** provisionar, conectar, validar, resetar e destruir via manifesto sem if/else por lab.
4. **G4 Pedagogia:** 4 labs com história, conceito, dica, 3 ou mais etapas validadas individualmente e progressão bloqueada.
5. **G5 Segurança:** testes adversariais sem falha crítica, incluindo escape, acesso cruzado, egress e fraude em validadores.
6. **G6 Piloto:** pelo menos 15 participantes, meta de 30 sessões simultâneas testada, P95 de ready <=60 s (meta), >=98% provisionamento válido (meta).

## 6. Decisões abertas

Inventário do host/cluster físico, virtualização disponível, licença/suporte, rede DMZ/egress, armazenamento, tamanho do piloto, níveis de dica e dedução de pontos, política de persistência ao reset. Registrar em `docs/ADR/` antes de comprar infraestrutura.
