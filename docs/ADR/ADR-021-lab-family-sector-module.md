# ADR-021: Família, ramo de atividade e módulo do curso nos laboratórios

- **Status:** Aceito pelo PO (2026-11-16, decisão por card: "lab próprio por ramo").
- **Data:** 2026-11-16
- **Relacionados:** ADR-006 (contrato do manifesto), ADR-016 (só a última versão no painel), ADR-017 (classificação)

## Contexto

A primeira leva de novos laboratórios (A1 XSS, A2 CSRF, A3 Upload + stored XSS, A4 senha/crypto e A5 mass assignment) foi pedida pelo PO em três variações por ramo de atividade dos clientes CECyber: Financeiro, Saúde e Indústria/Energia. A mecânica da vulnerabilidade e o validador são os mesmos; mudam a história, os nomes do domínio e os dados fictícios. O PO quer escolher os labs pelo ramo em que o aluno atua e identificar o módulo do curso Security Engineer (Foundation, Trained, Expert, Master) a que cada um se liga.

## Decisão

1. **Cada variação por ramo é um laboratório próprio** (LAB-005 a LAB-019), com manifesto, release, progresso e selo de conclusão próprios. Nada muda no motor de sessões, no progresso nem no histórico de versões.
2. **Três campos opcionais em `metadata`**, sem valor padrão serializado (o digest das releases existentes não muda):
   - `family`: slug da família, por exemplo `xss`, `csrf`, `upload`, `senha`, `mass-assignment`;
   - `sectors`: lista de ramos, valores `financeiro`, `saude`, `industria-energia`;
   - `courseModules`: módulos do curso, valores `foundation`, `trained`, `expert`, `master`.
3. **Catálogo e painel.** A API pública devolve `family`, `sectors` e `courseModules`. O painel ganha filtro por ramo e por módulo (lembrado no navegador do aluno); sem filtro, mostra tudo. O tutorial (LAB-000) aparece sempre. O catálogo de documentação mostra ramo, família e módulos.
4. **Código da família.** O título de cada lab traz o código `A1-FIN`, `A1-SAU`, `A1-IND` etc. O código-base comum fica descrito em `laboratories/_familias/<familia>/README.md`; cada lab continua autocontido na sua pasta (o build não muda), e a suíte de validação de cada ramo é gerada por uma função da família no registro protegido.

## Alternativa descartada

Um laboratório por família com a escolha do ramo na sessão: exigiria mudar motor, progresso e catálogo, e atrasaria a leva.

## Consequências

- Contrato: `Metadata.family`, `Metadata.sectors`, `Metadata.course_modules` (alias `courseModules`), enums `Sector` e `CourseModule`; schema reexportado.
- Labs anteriores (001 a 004) não aparecem quando há filtro de ramo, até ganharem os campos numa versão nova.
- Testes: contrato (aceitos, rejeitados, digest inalterado), integração (API devolve os campos) e unidade do filtro no portal.
