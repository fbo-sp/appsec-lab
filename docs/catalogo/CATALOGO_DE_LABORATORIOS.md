# Catálogo de laboratórios — CECyber AppSec Labs

> Arquivo **gerado** por `scripts/gen-catalogo.py` a partir dos manifestos em `laboratories/`
> e do histórico em `docs/catalogo/historico-versoes.yaml`. Não edite à mão: ao criar um lab ou
> publicar uma versão, atualize o histórico e rode o script. O CI falha se o catálogo estiver
> desatualizado (ADR-017).

Para professores e área comercial: escolha o laboratório pela aula conceitual (OWASP,
SANS CWE Top 25 ou CWE). Edições de referência: OWASP Top 10 2025 (anterior 2021),
OWASP API Security Top 10 2023 (anterior 2019) e SANS CWE Top 25 2025 (anterior 2024),
publicada pela MITRE com a CISA. Quando o lab não se enquadra numa lista, o CWE orienta a escolha.

## Comece por aqui: LAB-000 · Tutorial: conhecendo a plataforma de laboratórios

Tutorial da plataforma, sem vulnerabilidade e sem classificação.
Indicado como primeira atividade de qualquer turma, antes do primeiro laboratório.

- Versão vigente: 1.0.1
- Duração estimada: 10 min

### Etapas

1. Conhecer a tela (10 pts)
2. Usar a barra de endereço (15 pts)
3. Usar o terminal (15 pts)
4. Pedir uma dica (20 pts)
5. Editar o código e validar (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 0.1.0 | 2026-11-11 | 2026-11-12 | obsoleta | Primeira versão do lab benigno de verificação do motor. |
| 0.2.0 | 2026-11-12 | 2026-11-13 | obsoleta | Etapas com validação, progresso e dicas. |
| 0.2.1 | 2026-11-13 | 2026-11-15 | obsoleta | Texto da dica 1 ajustado às abas do workspace. |
| 1.0.0 | 2026-11-15 | 2026-11-15 | obsoleta | Vira o tutorial da plataforma, com 5 etapas sobre a tela, a barra de endereço, o terminal, as dicas e a validação. |
| 1.0.1 | 2026-11-15 | — | vigente | Etapa do terminal ganha um "Explorar mais" de exemplo, apresentando o estudo complementar opcional da plataforma. |

## Visão geral (versões vigentes)

| Lab | Título | Versão | CWE principal | OWASP Top 10 | SANS CWE Top 25 | Nível | Duração |
|---|---|---|---|---|---|---|---|
| LAB-001 | SQL Injection: a busca que expõe pacientes | 1.0.4 | CWE-89 | A05 Injection (2025) | #2 CWE-89 SQL Injection (2025) | Iniciante | 40 min |
| LAB-002 | IDOR: o comprovante que não era seu | 1.0.4 | CWE-639 | A01 Broken Access Control (2025) | #4 CWE-862 Missing Authorization (2025) | Iniciante | 40 min |
| LAB-003 | JWT: o token que ninguém conferiu | 1.0.3 | CWE-347 | A07 Authentication Failures (2025) | Não se enquadra; use o CWE (2025) | Iniciante | 45 min |
| LAB-004 | Command Injection: o teste de rede que virou terminal | 1.0.4 | CWE-78 | A05 Injection (2025) | #9 CWE-78 OS Command Injection (2025) | Iniciante | 40 min |
| LAB-005 | A1-FIN · XSS: a busca de favorecidos que rouba a sessão | 1.0.0 | CWE-79 | A05 Injection (2025) | #1 CWE-79 Cross-site Scripting (2025) | Iniciante | 40 min |
| LAB-006 | A1-SAU · XSS: a busca de exames que rouba o acesso aos laudos | 1.0.0 | CWE-79 | A05 Injection (2025) | #1 CWE-79 Cross-site Scripting (2025) | Iniciante | 40 min |
| LAB-007 | A1-IND · XSS: a ordem de serviço que executa no centro de operação | 1.0.0 | CWE-79 | A05 Injection (2025) | #1 CWE-79 Cross-site Scripting (2025) | Iniciante | 40 min |

## LAB-001 · SQL Injection: a busca que expõe pacientes

- Versão vigente: 1.0.4
- Cenário: Portal de agendamento com a busca "Encontre um médico"
- Papel do aluno: Desenvolvedor(a) do time de sistemas da Clínica VidaPlena
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min

### Classificação

- CWE: CWE-89
- OWASP Top 10 2025: A05 Injection
- OWASP Top 10 2021: A03 Injection
- SANS CWE Top 25 2025: #2 CWE-89 SQL Injection
- SANS CWE Top 25 2024: #3 CWE-89 SQL Injection

### Objetivos

- Seguir uma requisição pelas camadas de uma aplicação web até a consulta ao banco
- Entender por que concatenar texto em SQL transforma dado em código
- Demonstrar o impacto de uma SQL Injection com UNION em dados fictícios
- Corrigir a falha com consulta parametrizada sem quebrar a busca legítima

### Etapas

1. Conhecer a aplicação (10 pts)
2. Provocar um erro (15 pts)
3. Medir a consulta (15 pts)
4. Extrair dados sensíveis (20 pts)
5. Corrigir com consulta parametrizada (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-13 | 2026-11-13 | obsoleta | Primeira versão (SQL Injection, Clínica VidaPlena). |
| 1.0.1 | 2026-11-13 | 2026-11-15 | obsoleta | Trecho da correção com o recuo real do método (evita IndentationError). Aprovada pelo PO. |
| 1.0.2 | 2026-11-15 | 2026-11-15 | obsoleta | Classificação OWASP e SANS CWE Top 25; referência do OWASP Top 10 atualizada para 2025. |
| 1.0.3 | 2026-11-15 | 2026-11-15 | obsoleta | Texto das tarefas com só o necessário; verificação de log e solução de problemas movidas para "Explorar mais"; ataque a repetir mostrado por extenso na etapa 5. |
| 1.0.4 | 2026-11-15 | — | vigente | Leitura do log usa grep da linha útil em vez de tail (o /tmp/app.log também registra os acessos GET / 200, que escondiam a linha no tail). |

## LAB-002 · IDOR: o comprovante que não era seu

- Versão vigente: 1.0.4
- Cenário: Internet Banking, área "Meus comprovantes de PIX"
- Papel do aluno: Desenvolvedor(a) do time de canais digitais do Banco Vértice Digital
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min

### Classificação

- CWE: CWE-639 (principal), CWE-862
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- OWASP API Security Top 10 2023: API1 Broken Object Level Authorization
- OWASP API Security Top 10 2019: API1 Broken Object Level Authorization
- SANS CWE Top 25 2025: #4 CWE-862 Missing Authorization; #24 CWE-639 Authorization Bypass Through User-Controlled Key
- SANS CWE Top 25 2024: #9 CWE-862 Missing Authorization

### Objetivos

- Diferenciar autenticação (quem é você) de autorização (o que você pode ver)
- Reconhecer identificadores previsíveis em URLs e APIs
- Medir o impacto de um IDOR enumerando objetos de outros clientes
- Corrigir a falha verificando o dono do objeto no servidor, para a página e para a API

### Etapas

1. Conhecer a aplicação (10 pts)
2. Observar o identificador (15 pts)
3. Abrir o comprovante de outro cliente (15 pts)
4. Medir o impacto (20 pts)
5. Corrigir verificando o dono (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-13 | 2026-11-14 | obsoleta | Primeira versão (IDOR, Banco Vértice Digital). |
| 1.0.1 | 2026-11-14 | 2026-11-15 | obsoleta | Etapa 4 com contagem correta (34) e busca do PIX de R$ 487.900,00; etapa 2 explica a barra de endereço. |
| 1.0.2 | 2026-11-15 | 2026-11-15 | obsoleta | Classificação OWASP, OWASP API e SANS CWE Top 25; referência do OWASP Top 10 atualizada para 2025. |
| 1.0.3 | 2026-11-15 | 2026-11-15 | obsoleta | Texto das tarefas enxuto; log, pior caso do PIX e solução de problemas em "Explorar mais"; navegação pela barra de endereço explicitada na etapa 5. |
| 1.0.4 | 2026-11-15 | — | vigente | Leitura do log usa grep da linha útil em vez de tail (os acessos GET / 200 no /tmp/app.log escondiam a linha no tail). |

## LAB-003 · JWT: o token que ninguém conferiu

- Versão vigente: 1.0.3
- Cenário: API do Portal Orbe, usada pelo site e pelo aplicativo do cliente
- Papel do aluno: Desenvolvedor(a) do time de APIs da Orbe Cartões, emissora de cartões de crédito
- Linguagem / stack: javascript / express
- Nível: Iniciante · duração estimada: 45 min

### Classificação

- CWE: CWE-347 (principal), CWE-287
- OWASP Top 10 2025: A07 Authentication Failures (principal); A04 Cryptographic Failures
- OWASP Top 10 2021: A07 Identification and Authentication Failures (principal); A02 Cryptographic Failures
- OWASP API Security Top 10 2023: API2 Broken Authentication
- OWASP API Security Top 10 2019: API2 Broken User Authentication
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: #14 CWE-287 Improper Authentication

### Objetivos

- Entender a estrutura de um JWT (cabeçalho, dados e assinatura) e por que ele não é criptografado
- Diferenciar decodificar um token de verificar um token
- Forjar um token para demonstrar o impacto em dados fictícios
- Corrigir a validação conferindo assinatura, algoritmo e validade

### Etapas

1. Conhecer a aplicação (10 pts)
2. Ler o conteúdo do token (15 pts)
3. Forjar um token de gerente (15 pts)
4. Medir o impacto (20 pts)
5. Corrigir verificando a assinatura (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-13 | 2026-11-15 | obsoleta | Primeira versão (JWT sem verificação de assinatura, Orbe Cartões, Node.js). |
| 1.0.1 | 2026-11-15 | 2026-11-15 | obsoleta | Classificação OWASP, OWASP API e SANS CWE Top 25; referência ao OWASP Top 10:2025 A07. |
| 1.0.2 | 2026-11-15 | 2026-11-15 | obsoleta | Etapas 4 e 5 com só o necessário na tarefa; leitura do log e solução de problemas em "Explorar mais"; relogin na aba Aplicação explicitado (Sair e entrar com as credenciais da Larissa, da etapa 1). |
| 1.0.3 | 2026-11-15 | — | vigente | Leitura do log usa grep da linha útil, por exemplo grep da mensagem "Limite alterado", em vez de tail, porque os acessos GET / 200 no /tmp/app.log escondiam a linha. |

## LAB-004 · Command Injection: o teste de rede que virou terminal

- Versão vigente: 1.0.4
- Cenário: Portal de Manutenção da Planta Contagem, com o teste de comunicação com CLPs
- Papel do aluno: Desenvolvedor(a) do time de sistemas industriais da Ferrara Metais
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min

### Classificação

- CWE: CWE-78
- OWASP Top 10 2025: A05 Injection
- OWASP Top 10 2021: A03 Injection
- SANS CWE Top 25 2025: #9 CWE-78 OS Command Injection
- SANS CWE Top 25 2024: #7 CWE-78 OS Command Injection

### Objetivos

- Reconhecer quando uma aplicação repassa dados do usuário para o shell do sistema operacional
- Entender o papel dos metacaracteres do shell, como ponto e vírgula, pipe e $( )
- Demonstrar o impacto lendo um arquivo sensível fictício da planta
- Corrigir a falha validando a entrada e executando o programa sem shell, com lista de argumentos

### Etapas

1. Conhecer a aplicação (10 pts)
2. Encadear um comando (15 pts)
3. Explorar o servidor (15 pts)
4. Medir o impacto (20 pts)
5. Corrigir sem shell e com validação (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-13 | 2026-11-13 | obsoleta | Primeira versão (Command Injection, Ferrara Metais). |
| 1.0.1 | 2026-11-13 | 2026-11-15 | obsoleta | Correção do fim de linha (CRLF) que quebrava o diag-clp no Windows. |
| 1.0.2 | 2026-11-15 | 2026-11-15 | obsoleta | Classificação OWASP e SANS CWE Top 25; referência do OWASP Top 10 atualizada para 2025. |
| 1.0.3 | 2026-11-15 | 2026-11-15 | obsoleta | Texto das tarefas enxuto; leitura do log e solução de problemas em "Explorar mais"; ataque a repetir mostrado por extenso na etapa 5. |
| 1.0.4 | 2026-11-15 | — | vigente | Leitura do log usa grep da linha útil, por exemplo grep da mensagem "Executando", em vez de tail, porque os acessos GET / 200 no /tmp/app.log escondiam a linha. |

## LAB-005 · A1-FIN · XSS: a busca de favorecidos que rouba a sessão

- Versão vigente: 1.0.0
- Cenário: Internet Banking, telas "Meus favorecidos" e "Painel antifraude"
- Papel do aluno: Desenvolvedor(a) do time de canais digitais do Banco Aurora Digital
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: xss
- Ramo: Financeiro
- Módulo do curso: Trained, MASTER

### Classificação

- CWE: CWE-79
- OWASP Top 10 2025: A05 Injection
- OWASP Top 10 2021: A03 Injection
- SANS CWE Top 25 2025: #1 CWE-79 Cross-site Scripting
- SANS CWE Top 25 2024: #1 CWE-79 Cross-site Scripting

### Objetivos

- Seguir o texto digitado pelo usuário desde o formulário até o HTML da resposta
- Entender por que uma lista de bloqueio (remover <script>) não impede XSS
- Demonstrar XSS refletido e armazenado lendo cookies sem HttpOnly, com dados fictícios
- Corrigir a falha deixando o Jinja2 codificar a saída, sem quebrar a busca legítima

### Etapas

1. Conhecer a aplicação (10 pts)
2. Testar a proteção do time (15 pts)
3. Executar JavaScript pela busca (20 pts)
4. Atingir a equipe com XSS armazenado (15 pts)
5. Corrigir codificando a saída (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (XSS refletido e armazenado, Banco Aurora Digital; família xss, ramo Financeiro). |

## LAB-006 · A1-SAU · XSS: a busca de exames que rouba o acesso aos laudos

- Versão vigente: 1.0.0
- Cenário: Portal do Paciente, telas "Meus exames" e "Fila de atendimento"
- Papel do aluno: Desenvolvedor(a) do time de produtos digitais da Rede Lumina Diagnósticos
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: xss
- Ramo: Saúde
- Módulo do curso: Trained, MASTER

### Classificação

- CWE: CWE-79
- OWASP Top 10 2025: A05 Injection
- OWASP Top 10 2021: A03 Injection
- SANS CWE Top 25 2025: #1 CWE-79 Cross-site Scripting
- SANS CWE Top 25 2024: #1 CWE-79 Cross-site Scripting

### Objetivos

- Seguir o texto digitado pelo usuário desde o formulário até o HTML da resposta
- Entender por que uma lista de bloqueio (remover <script>) não impede XSS
- Demonstrar XSS refletido e armazenado lendo cookies sem HttpOnly, com dados fictícios
- Corrigir a falha deixando o Jinja2 codificar a saída, sem quebrar a busca legítima

### Etapas

1. Conhecer a aplicação (10 pts)
2. Testar a proteção do time (15 pts)
3. Executar JavaScript pela busca (20 pts)
4. Atingir a equipe com XSS armazenado (15 pts)
5. Corrigir codificando a saída (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (XSS refletido e armazenado, Rede Lumina Diagnósticos; família xss, ramo Saúde). |

## LAB-007 · A1-IND · XSS: a ordem de serviço que executa no centro de operação

- Versão vigente: 1.0.0
- Cenário: Portal de Chamados de Campo, telas "Minhas ordens" e "Painel do Centro de Operação"
- Papel do aluno: Desenvolvedor(a) do time de sistemas de operação da Voltera Distribuidora de Energia
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: xss
- Ramo: Indústria e Energia
- Módulo do curso: Trained, MASTER

### Classificação

- CWE: CWE-79
- OWASP Top 10 2025: A05 Injection
- OWASP Top 10 2021: A03 Injection
- SANS CWE Top 25 2025: #1 CWE-79 Cross-site Scripting
- SANS CWE Top 25 2024: #1 CWE-79 Cross-site Scripting

### Objetivos

- Seguir o texto digitado pelo usuário desde o formulário até o HTML da resposta
- Entender por que uma lista de bloqueio (remover <script>) não impede XSS
- Demonstrar XSS refletido e armazenado lendo cookies sem HttpOnly, com dados fictícios
- Corrigir a falha deixando o Jinja2 codificar a saída, sem quebrar a busca legítima

### Etapas

1. Conhecer a aplicação (10 pts)
2. Testar a proteção do time (15 pts)
3. Executar JavaScript pela busca (20 pts)
4. Atingir a equipe com XSS armazenado (15 pts)
5. Corrigir codificando a saída (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (XSS refletido e armazenado, Voltera Distribuidora de Energia; família xss, ramo Indústria e Energia). |
