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
| LAB-008 | A5-FIN · Mass Assignment: o perfil que vira analista de crédito | 1.0.0 | CWE-915 | A08 Software or Data Integrity Failures (2025) | Não se enquadra; use o CWE (2025) | Iniciante | 35 min |
| LAB-009 | A5-SAU · Mass Assignment: o beneficiário que trocou o próprio plano | 1.0.0 | CWE-915 | A08 Software or Data Integrity Failures (2025) | Não se enquadra; use o CWE (2025) | Iniciante | 35 min |
| LAB-010 | A5-IND · Mass Assignment: o fornecedor que se aprovou sozinho | 1.0.0 | CWE-915 | A08 Software or Data Integrity Failures (2025) | Não se enquadra; use o CWE (2025) | Iniciante | 35 min |
| LAB-011 | A2-FIN · CSRF: a chave PIX trocada pelo e-mail de campanha | 1.0.0 | CWE-352 | A01 Broken Access Control (2025) | #3 CWE-352 Cross-Site Request Forgery (CSRF) (2025) | Iniciante | 40 min |
| LAB-012 | A2-SAU · CSRF: o laudo que foi para o e-mail errado | 1.0.0 | CWE-352 | A01 Broken Access Control (2025) | #3 CWE-352 Cross-Site Request Forgery (CSRF) (2025) | Iniciante | 40 min |
| LAB-013 | A2-IND · CSRF: o alarme da comporta que foi para outro celular | 1.0.0 | CWE-352 | A01 Broken Access Control (2025) | #3 CWE-352 Cross-Site Request Forgery (CSRF) (2025) | Iniciante | 40 min |
| LAB-014 | A3-FIN · Upload: o comprovante de renda que virou página | 1.0.0 | CWE-434 | A06 Insecure Design (2025) | #12 CWE-434 Unrestricted Upload of File with Dangerous Type (2025) | Iniciante | 45 min |
| LAB-015 | A3-SAU · Upload: o pedido médico que virou página | 1.0.0 | CWE-434 | A06 Insecure Design (2025) | #12 CWE-434 Unrestricted Upload of File with Dangerous Type (2025) | Iniciante | 45 min |
| LAB-016 | A3-IND · Upload: a nota fiscal do fornecedor que virou página | 1.0.0 | CWE-434 | A06 Insecure Design (2025) | #12 CWE-434 Unrestricted Upload of File with Dangerous Type (2025) | Iniciante | 45 min |
| LAB-017 | A4-FIN · Senhas: as senhas MD5 herdadas da fusão | 1.0.0 | CWE-916 | A04 Cryptographic Failures (2025) | Não se enquadra; use o CWE (2025) | Iniciante | 40 min |
| LAB-018 | A4-SAU · Senhas: o portal do paciente com senhas em MD5 | 1.0.0 | CWE-916 | A04 Cryptographic Failures (2025) | Não se enquadra; use o CWE (2025) | Iniciante | 40 min |
| LAB-019 | A4-IND · Senhas: o portal do colaborador com senhas em MD5 | 1.0.0 | CWE-916 | A04 Cryptographic Failures (2025) | Não se enquadra; use o CWE (2025) | Iniciante | 40 min |
| LAB-020 | A6-FIN · SSRF: o importador de comprovantes que busca qualquer URL | 1.0.0 | CWE-918 | A01 Broken Access Control (2025) | #22 CWE-918 (2025) | Intermediário | 40 min |
| LAB-021 | A6-SAU · SSRF: o importador de laudos que busca qualquer URL | 1.0.0 | CWE-918 | A01 Broken Access Control (2025) | #22 CWE-918 (2025) | Intermediário | 40 min |
| LAB-022 | A6-IND · SSRF: o importador de documentos técnicos que busca qualquer URL | 1.0.0 | CWE-918 | A01 Broken Access Control (2025) | #22 CWE-918 (2025) | Intermediário | 40 min |
| LAB-023 | A8-FIN · Lógica de negócio: o resgate que aceita qualquer valor | 1.0.0 | CWE-840 | A06 Insecure Design (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-024 | A8-SAU · Lógica de negócio: o reembolso que aceita qualquer valor | 1.0.0 | CWE-840 | A06 Insecure Design (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-025 | A8-IND · Lógica de negócio: o uso de créditos que aceita qualquer valor | 1.0.0 | CWE-840 | A06 Insecure Design (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-026 | A13-FIN · Força bruta no login: o login que aceita senhas sem parar | 1.0.0 | CWE-307 | A07 Authentication Failures (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-027 | A13-SAU · Força bruta no login: o login que aceita senhas sem parar | 1.0.0 | CWE-307 | A07 Authentication Failures (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-028 | A13-IND · Força bruta no login: o login que aceita senhas sem parar | 1.0.0 | CWE-307 | A07 Authentication Failures (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-029 | A7-FIN · CORS mal configurado: o perfil que qualquer site pode ler | 1.0.0 | CWE-942 | A02 Security Misconfiguration (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-030 | A7-SAU · CORS mal configurado: o perfil que qualquer site pode ler | 1.0.0 | CWE-942 | A02 Security Misconfiguration (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-031 | A7-IND · CORS mal configurado: o perfil que qualquer site pode ler | 1.0.0 | CWE-942 | A02 Security Misconfiguration (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-032 | A12-FIN · Path traversal: o documento que foge da pasta | 1.0.0 | CWE-22 | A01 Broken Access Control (2025) | #6 CWE-22 Path Traversal (2025) | Intermediário | 35 min |
| LAB-033 | A12-SAU · Path traversal: o documento que foge da pasta | 1.0.0 | CWE-22 | A01 Broken Access Control (2025) | #6 CWE-22 Path Traversal (2025) | Intermediário | 35 min |
| LAB-034 | A12-IND · Path traversal: o documento que foge da pasta | 1.0.0 | CWE-22 | A01 Broken Access Control (2025) | #6 CWE-22 Path Traversal (2025) | Intermediário | 35 min |
| LAB-035 | A10-FIN · Confiança no cliente: a loja que confia no preço do cliente | 1.0.0 | CWE-602 | A06 Insecure Design (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-036 | A10-SAU · Confiança no cliente: a loja que confia no preço do cliente | 1.0.0 | CWE-602 | A06 Insecure Design (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-037 | A10-IND · Confiança no cliente: a loja que confia no preço do cliente | 1.0.0 | CWE-602 | A06 Insecure Design (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 35 min |
| LAB-038 | A15-FIN · Autorização de função: a API de admin aberta para todos | 1.0.0 | CWE-862 | A01 Broken Access Control (2025) | #4 CWE-862 Missing Authorization (2025) | Intermediário | 35 min |
| LAB-039 | A15-SAU · Autorização de função: a API de admin aberta para todos | 1.0.0 | CWE-862 | A01 Broken Access Control (2025) | #4 CWE-862 Missing Authorization (2025) | Intermediário | 35 min |
| LAB-040 | A15-IND · Autorização de função: a API de admin aberta para todos | 1.0.0 | CWE-862 | A01 Broken Access Control (2025) | #4 CWE-862 Missing Authorization (2025) | Intermediário | 35 min |
| LAB-041 | A19-FIN · Erros verbosos: a API que mostra o traceback | 1.0.0 | CWE-209 | A10 Mishandling of Exceptional Conditions (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 30 min |
| LAB-042 | A19-SAU · Erros verbosos: a API que mostra o traceback | 1.0.0 | CWE-209 | A10 Mishandling of Exceptional Conditions (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 30 min |
| LAB-043 | A19-IND · Erros verbosos: a API que mostra o traceback | 1.0.0 | CWE-209 | A10 Mishandling of Exceptional Conditions (2025) | Não se enquadra; use o CWE (2025) | Intermediário | 30 min |

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

## LAB-008 · A5-FIN · Mass Assignment: o perfil que vira analista de crédito

- Versão vigente: 1.0.0
- Cenário: App Trilha Pay, tela "Meu perfil" e a API /api/perfil
- Papel do aluno: Desenvolvedor(a) do squad de conta digital da Trilha Pay
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 35 min
- Família: mass-assignment
- Ramo: Financeiro
- Módulo do curso: MASTER

### Classificação

- CWE: CWE-915
- OWASP Top 10 2025: A08 Software or Data Integrity Failures
- OWASP Top 10 2021: A08 Software and Data Integrity Failures
- OWASP API Security Top 10 2023: API3 Broken Object Property Level Authorization
- OWASP API Security Top 10 2019: API6 Mass Assignment
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Ler uma API JSON e descobrir quais campos o servidor guarda para cada usuário
- Entender por que repassar o corpo inteiro da requisição para o banco permite alterar campos protegidos
- Elevar o próprio benefício e o próprio perfil de acesso com uma única requisição, com dados fictícios
- Corrigir a falha com uma lista de campos permitidos no serviço, sem quebrar a edição legítima

### Etapas

1. Conhecer a tela Meu perfil (10 pts)
2. Seguir o JSON até o banco (15 pts)
3. Mudar o próprio pacote da conta (20 pts)
4. Virar analista (15 pts)
5. Corrigir com uma lista de campos permitidos (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (Mass Assignment na API de perfil, Trilha Pay; família mass-assignment, ramo Financeiro). |

## LAB-009 · A5-SAU · Mass Assignment: o beneficiário que trocou o próprio plano

- Versão vigente: 1.0.0
- Cenário: Portal do Beneficiário, tela "Meu perfil" e a API /api/perfil
- Papel do aluno: Desenvolvedor(a) do time de canais digitais da Sereno Saúde
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 35 min
- Família: mass-assignment
- Ramo: Saúde
- Módulo do curso: MASTER

### Classificação

- CWE: CWE-915
- OWASP Top 10 2025: A08 Software or Data Integrity Failures
- OWASP Top 10 2021: A08 Software and Data Integrity Failures
- OWASP API Security Top 10 2023: API3 Broken Object Property Level Authorization
- OWASP API Security Top 10 2019: API6 Mass Assignment
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Ler uma API JSON e descobrir quais campos o servidor guarda para cada usuário
- Entender por que repassar o corpo inteiro da requisição para o banco permite alterar campos protegidos
- Elevar o próprio benefício e o próprio perfil de acesso com uma única requisição, com dados fictícios
- Corrigir a falha com uma lista de campos permitidos no serviço, sem quebrar a edição legítima

### Etapas

1. Conhecer a tela Meu perfil (10 pts)
2. Seguir o JSON até o banco (15 pts)
3. Mudar o próprio plano (20 pts)
4. Virar auditor (15 pts)
5. Corrigir com uma lista de campos permitidos (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (Mass Assignment na API de perfil, Sereno Saúde; família mass-assignment, ramo Saúde). |

## LAB-010 · A5-IND · Mass Assignment: o fornecedor que se aprovou sozinho

- Versão vigente: 1.0.0
- Cenário: Portal de Fornecedores, tela "Meu perfil" e a API /api/perfil
- Papel do aluno: Desenvolvedor(a) do time de sistemas corporativos da Termoverde Geração
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 35 min
- Família: mass-assignment
- Ramo: Indústria e Energia
- Módulo do curso: MASTER

### Classificação

- CWE: CWE-915
- OWASP Top 10 2025: A08 Software or Data Integrity Failures
- OWASP Top 10 2021: A08 Software and Data Integrity Failures
- OWASP API Security Top 10 2023: API3 Broken Object Property Level Authorization
- OWASP API Security Top 10 2019: API6 Mass Assignment
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Ler uma API JSON e descobrir quais campos o servidor guarda para cada usuário
- Entender por que repassar o corpo inteiro da requisição para o banco permite alterar campos protegidos
- Elevar o próprio benefício e o próprio perfil de acesso com uma única requisição, com dados fictícios
- Corrigir a falha com uma lista de campos permitidos no serviço, sem quebrar a edição legítima

### Etapas

1. Conhecer a tela Meu perfil (10 pts)
2. Seguir o JSON até o banco (15 pts)
3. Mudar o próprio categoria do fornecedor (20 pts)
4. Virar comprador (15 pts)
5. Corrigir com uma lista de campos permitidos (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (Mass Assignment na API de perfil, Termoverde Geração; família mass-assignment, ramo Indústria e Energia). |

## LAB-011 · A2-FIN · CSRF: a chave PIX trocada pelo e-mail de campanha

- Versão vigente: 1.0.0
- Cenário: Portal do Segurado, tela "Conta para indenização"
- Papel do aluno: Desenvolvedor(a) da squad do Portal do Segurado da Vínculo Seguros
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: csrf
- Ramo: Financeiro
- Módulo do curso: Trained

### Classificação

- CWE: CWE-352
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- SANS CWE Top 25 2025: #3 CWE-352 Cross-Site Request Forgery (CSRF)
- SANS CWE Top 25 2024: #4 CWE-352 Cross-Site Request Forgery (CSRF)

### Objetivos

- Entender por que o navegador envia o cookie de sessão em requisições que o usuário não pediu
- Diferenciar site de origem e saber o que o atributo SameSite protege e o que não protege
- Demonstrar CSRF com uma página fictícia de atacante e achar a evidência no log
- Corrigir a falha com um token anti-CSRF por sessão, sem quebrar o uso legítimo

### Etapas

1. Conhecer a tela Conta para indenização (10 pts)
2. Entender a proteção que o time colocou (15 pts)
3. Abrir a página do atacante (20 pts)
4. Achar a evidência no log (15 pts)
5. Corrigir com um token anti-CSRF (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (CSRF na troca da chave PIX de indenização, Vínculo Seguros; família csrf, ramo Financeiro). |

## LAB-012 · A2-SAU · CSRF: o laudo que foi para o e-mail errado

- Versão vigente: 1.0.0
- Cenário: Portal do Paciente, tela "Envio de laudos"
- Papel do aluno: Desenvolvedor(a) do time de canais digitais da Vitalis Hospitais
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: csrf
- Ramo: Saúde
- Módulo do curso: Trained

### Classificação

- CWE: CWE-352
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- SANS CWE Top 25 2025: #3 CWE-352 Cross-Site Request Forgery (CSRF)
- SANS CWE Top 25 2024: #4 CWE-352 Cross-Site Request Forgery (CSRF)

### Objetivos

- Entender por que o navegador envia o cookie de sessão em requisições que o usuário não pediu
- Diferenciar site de origem e saber o que o atributo SameSite protege e o que não protege
- Demonstrar CSRF com uma página fictícia de atacante e achar a evidência no log
- Corrigir a falha com um token anti-CSRF por sessão, sem quebrar o uso legítimo

### Etapas

1. Conhecer a tela Envio de laudos (10 pts)
2. Entender a proteção que o time colocou (15 pts)
3. Abrir a página do atacante (20 pts)
4. Achar a evidência no log (15 pts)
5. Corrigir com um token anti-CSRF (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (CSRF na troca do e-mail de laudos, Vitalis Hospitais; família csrf, ramo Saúde). |

## LAB-013 · A2-IND · CSRF: o alarme da comporta que foi para outro celular

- Versão vigente: 1.0.0
- Cenário: Supervisório web da PCH Rio Claro, tela "Plantão de alarmes"
- Papel do aluno: Desenvolvedor(a) do time de automação da Correnteza Geração
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: csrf
- Ramo: Indústria e Energia
- Módulo do curso: Trained

### Classificação

- CWE: CWE-352
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- SANS CWE Top 25 2025: #3 CWE-352 Cross-Site Request Forgery (CSRF)
- SANS CWE Top 25 2024: #4 CWE-352 Cross-Site Request Forgery (CSRF)

### Objetivos

- Entender por que o navegador envia o cookie de sessão em requisições que o usuário não pediu
- Diferenciar site de origem e saber o que o atributo SameSite protege e o que não protege
- Demonstrar CSRF com uma página fictícia de atacante e achar a evidência no log
- Corrigir a falha com um token anti-CSRF por sessão, sem quebrar o uso legítimo

### Etapas

1. Conhecer a tela Plantão de alarmes (10 pts)
2. Entender a proteção que o time colocou (15 pts)
3. Abrir a página do atacante (20 pts)
4. Achar a evidência no log (15 pts)
5. Corrigir com um token anti-CSRF (40 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (CSRF na troca do celular do plantão de alarmes, Correnteza Geração; família csrf, ramo Indústria e Energia). |

## LAB-014 · A3-FIN · Upload: o comprovante de renda que virou página

- Versão vigente: 1.0.0
- Cenário: portal Mesa de Crédito, onde o cooperado anexa comprovantes para análise
- Papel do aluno: Pessoa desenvolvedora da squad de crédito da Cooperativa Credimova
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 45 min
- Família: upload
- Ramo: Financeiro
- Módulo do curso: Foundation, Trained

### Classificação

- CWE: CWE-434 (principal), CWE-79
- OWASP Top 10 2025: A06 Insecure Design; A05 Injection
- OWASP Top 10 2021: A04 Insecure Design; A03 Injection
- SANS CWE Top 25 2025: #12 CWE-434 Unrestricted Upload of File with Dangerous Type
- SANS CWE Top 25 2024: #10 CWE-434 Unrestricted Upload of File with Dangerous Type

### Objetivos

- Entender por que confiar no tipo informado pelo navegador (Content-Type) não valida um arquivo
- Enviar um arquivo HTML disfarçado e ver a aplicação servi-lo como página na própria origem
- Reconhecer o impacto (XSS armazenado) de um upload servido como HTML para a equipe interna
- Corrigir validando o conteúdo pela assinatura do arquivo, renomeando e impedindo a interpretação como HTML

### Etapas

1. Conhecer o envio de comprovantes de renda (10 pts)
2. Enviar um HTML disfarçado de imagem (15 pts)
3. Ver o arquivo ser servido como página (15 pts)
4. Saber como reconhecer o arquivo de verdade (15 pts)
5. Corrigir a validação do upload (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (upload irrestrito levando a XSS armazenado, Cooperativa Credimova; família upload, ramo Financeiro). |

## LAB-015 · A3-SAU · Upload: o pedido médico que virou página

- Versão vigente: 1.0.0
- Cenário: Portal de Agendamento, onde o paciente anexa o pedido médico do exame
- Papel do aluno: Pessoa desenvolvedora do time de sistemas da Clínica Sampaio
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 45 min
- Família: upload
- Ramo: Saúde
- Módulo do curso: Foundation, Trained

### Classificação

- CWE: CWE-434 (principal), CWE-79
- OWASP Top 10 2025: A06 Insecure Design; A05 Injection
- OWASP Top 10 2021: A04 Insecure Design; A03 Injection
- SANS CWE Top 25 2025: #12 CWE-434 Unrestricted Upload of File with Dangerous Type
- SANS CWE Top 25 2024: #10 CWE-434 Unrestricted Upload of File with Dangerous Type

### Objetivos

- Entender por que confiar no tipo informado pelo navegador (Content-Type) não valida um arquivo
- Enviar um arquivo HTML disfarçado e ver a aplicação servi-lo como página na própria origem
- Reconhecer o impacto (XSS armazenado) de um upload servido como HTML para a equipe interna
- Corrigir validando o conteúdo pela assinatura do arquivo, renomeando e impedindo a interpretação como HTML

### Etapas

1. Conhecer o envio de pedidos médicos (10 pts)
2. Enviar um HTML disfarçado de imagem (15 pts)
3. Ver o arquivo ser servido como página (15 pts)
4. Saber como reconhecer o arquivo de verdade (15 pts)
5. Corrigir a validação do upload (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (upload irrestrito levando a XSS armazenado, Clínica Sampaio; família upload, ramo Saúde). |

## LAB-016 · A3-IND · Upload: a nota fiscal do fornecedor que virou página

- Versão vigente: 1.0.0
- Cenário: Portal de Fornecedores, onde o fornecedor anexa a nota fiscal do pedido
- Papel do aluno: Pessoa desenvolvedora do time de compras da Siderúrgica Pindorama
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 45 min
- Família: upload
- Ramo: Indústria e Energia
- Módulo do curso: Foundation, Trained

### Classificação

- CWE: CWE-434 (principal), CWE-79
- OWASP Top 10 2025: A06 Insecure Design; A05 Injection
- OWASP Top 10 2021: A04 Insecure Design; A03 Injection
- SANS CWE Top 25 2025: #12 CWE-434 Unrestricted Upload of File with Dangerous Type
- SANS CWE Top 25 2024: #10 CWE-434 Unrestricted Upload of File with Dangerous Type

### Objetivos

- Entender por que confiar no tipo informado pelo navegador (Content-Type) não valida um arquivo
- Enviar um arquivo HTML disfarçado e ver a aplicação servi-lo como página na própria origem
- Reconhecer o impacto (XSS armazenado) de um upload servido como HTML para a equipe interna
- Corrigir validando o conteúdo pela assinatura do arquivo, renomeando e impedindo a interpretação como HTML

### Etapas

1. Conhecer o envio de notas fiscais (10 pts)
2. Enviar um HTML disfarçado de imagem (15 pts)
3. Ver o arquivo ser servido como página (15 pts)
4. Saber como reconhecer o arquivo de verdade (15 pts)
5. Corrigir a validação do upload (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (upload irrestrito levando a XSS armazenado, Siderúrgica Pindorama; família upload, ramo Indústria e Energia). |

## LAB-017 · A4-FIN · Senhas: as senhas MD5 herdadas da fusão

- Versão vigente: 1.0.0
- Cenário: portal Acesso Cooperado, onde o cooperado entra para ver conta e serviços
- Papel do aluno: Pessoa desenvolvedora da squad de canais digitais da Cooperativa Credimova
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: senha
- Ramo: Financeiro
- Módulo do curso: Foundation, Trained

### Classificação

- CWE: CWE-916 (principal), CWE-759, CWE-327
- OWASP Top 10 2025: A04 Cryptographic Failures
- OWASP Top 10 2021: A02 Cryptographic Failures
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que uma senha nunca é guardada como texto, e sim como um resumo (hash)
- Reconhecer por que MD5 (rápido e sem sal) não serve para senha
- Confirmar, no banco, que senhas iguais viram hashes iguais e que o resumo legado é reversível na prática
- Corrigir adotando um hash forte (com sal e custo) e migrando as contas antigas sem quebrar o login

### Etapas

1. Conhecer o login e achar onde a senha é conferida (10 pts)
2. Ver por que esse resumo não protege (15 pts)
3. Confirmar que o resumo legado é reversível na prática (15 pts)
4. Escolher o resumo certo para senha (15 pts)
5. Corrigir o armazenamento da senha (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (armazenamento inseguro de senha em MD5, Cooperativa Credimova; família senha, ramo Financeiro). |

## LAB-018 · A4-SAU · Senhas: o portal do paciente com senhas em MD5

- Versão vigente: 1.0.0
- Cenário: Portal do Paciente, onde o paciente entra para ver resultados de exames
- Papel do aluno: Pessoa desenvolvedora do time de produtos digitais dos Laboratórios Helios
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: senha
- Ramo: Saúde
- Módulo do curso: Foundation, Trained

### Classificação

- CWE: CWE-916 (principal), CWE-759, CWE-327
- OWASP Top 10 2025: A04 Cryptographic Failures
- OWASP Top 10 2021: A02 Cryptographic Failures
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que uma senha nunca é guardada como texto, e sim como um resumo (hash)
- Reconhecer por que MD5 (rápido e sem sal) não serve para senha
- Confirmar, no banco, que senhas iguais viram hashes iguais e que o resumo legado é reversível na prática
- Corrigir adotando um hash forte (com sal e custo) e migrando as contas antigas sem quebrar o login

### Etapas

1. Conhecer o login e achar onde a senha é conferida (10 pts)
2. Ver por que esse resumo não protege (15 pts)
3. Confirmar que o resumo legado é reversível na prática (15 pts)
4. Escolher o resumo certo para senha (15 pts)
5. Corrigir o armazenamento da senha (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (armazenamento inseguro de senha em MD5, Laboratórios Helios; família senha, ramo Saúde). |

## LAB-019 · A4-IND · Senhas: o portal do colaborador com senhas em MD5

- Versão vigente: 1.0.0
- Cenário: Portal do Colaborador, onde o funcionário entra para holerite, férias e benefícios
- Papel do aluno: Pessoa desenvolvedora do time de sistemas internos da Siderúrgica Pindorama
- Linguagem / stack: python / flask
- Nível: Iniciante · duração estimada: 40 min
- Família: senha
- Ramo: Indústria e Energia
- Módulo do curso: Foundation, Trained

### Classificação

- CWE: CWE-916 (principal), CWE-759, CWE-327
- OWASP Top 10 2025: A04 Cryptographic Failures
- OWASP Top 10 2021: A02 Cryptographic Failures
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que uma senha nunca é guardada como texto, e sim como um resumo (hash)
- Reconhecer por que MD5 (rápido e sem sal) não serve para senha
- Confirmar, no banco, que senhas iguais viram hashes iguais e que o resumo legado é reversível na prática
- Corrigir adotando um hash forte (com sal e custo) e migrando as contas antigas sem quebrar o login

### Etapas

1. Conhecer o login e achar onde a senha é conferida (10 pts)
2. Ver por que esse resumo não protege (15 pts)
3. Confirmar que o resumo legado é reversível na prática (15 pts)
4. Escolher o resumo certo para senha (15 pts)
5. Corrigir o armazenamento da senha (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-16 | — | vigente | Primeira versão (armazenamento inseguro de senha em MD5, Siderúrgica Pindorama; família senha, ramo Indústria e Energia). |

## LAB-020 · A6-FIN · SSRF: o importador de comprovantes que busca qualquer URL

- Versão vigente: 1.0.0
- Cenário: Mesa de Crédito, onde a equipe importa o comprovante de renda enviado pelo parceiro para analisar a proposta
- Papel do aluno: Pessoa desenvolvedora da squad de crédito da Cooperativa Credimova
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 40 min
- Família: ssrf
- Ramo: Financeiro
- Módulo do curso: Trained, MASTER

### Classificação

- CWE: CWE-918
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A10 Server-Side Request Forgery (SSRF)
- OWASP API Security Top 10 2023: API7 Server Side Request Forgery
- SANS CWE Top 25 2025: #22 CWE-918
- SANS CWE Top 25 2024: #19 CWE-918

### Objetivos

- Entender o que é SSRF: fazer o servidor da aplicação buscar uma URL escolhida por quem ataca
- Explorar a falha usando o importador para ler um serviço interno que o usuário não deveria alcançar
- Entender por que "é só uma busca de documento" vira acesso à infraestrutura interna
- Corrigir com uma lista de permissão (allowlist) de destinos, validada no servidor

### Etapas

1. Conhecer a Mesa e achar onde o servidor busca a URL (10 pts)
2. Usar o importador para ler um serviço interno (15 pts)
3. Ver que o importador não distingue destino nenhum (15 pts)
4. Escolher a defesa certa contra SSRF (15 pts)
5. Corrigir o importador com uma lista de permissão (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (SSRF no importador por URL, Cooperativa Credimova; família ssrf, ramo Financeiro). |

## LAB-021 · A6-SAU · SSRF: o importador de laudos que busca qualquer URL

- Versão vigente: 1.0.0
- Cenário: Central de Laudos, onde a recepção importa o laudo enviado pelo laboratório parceiro
- Papel do aluno: Pessoa desenvolvedora do time de sistemas da Clínica Sampaio
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 40 min
- Família: ssrf
- Ramo: Saúde
- Módulo do curso: Trained, MASTER

### Classificação

- CWE: CWE-918
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A10 Server-Side Request Forgery (SSRF)
- OWASP API Security Top 10 2023: API7 Server Side Request Forgery
- SANS CWE Top 25 2025: #22 CWE-918
- SANS CWE Top 25 2024: #19 CWE-918

### Objetivos

- Entender o que é SSRF: fazer o servidor da aplicação buscar uma URL escolhida por quem ataca
- Explorar a falha usando o importador para ler um serviço interno que o usuário não deveria alcançar
- Entender por que "é só uma busca de documento" vira acesso à infraestrutura interna
- Corrigir com uma lista de permissão (allowlist) de destinos, validada no servidor

### Etapas

1. Conhecer a Mesa e achar onde o servidor busca a URL (10 pts)
2. Usar o importador para ler um serviço interno (15 pts)
3. Ver que o importador não distingue destino nenhum (15 pts)
4. Escolher a defesa certa contra SSRF (15 pts)
5. Corrigir o importador com uma lista de permissão (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (SSRF no importador por URL, Clínica Sampaio; família ssrf, ramo Saúde). |

## LAB-022 · A6-IND · SSRF: o importador de documentos técnicos que busca qualquer URL

- Versão vigente: 1.0.0
- Cenário: Portal de Engenharia, onde a equipe importa o documento técnico enviado pelo fornecedor
- Papel do aluno: Pessoa desenvolvedora do time de sistemas industriais da Siderúrgica Pindorama
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 40 min
- Família: ssrf
- Ramo: Indústria e Energia
- Módulo do curso: Trained, MASTER

### Classificação

- CWE: CWE-918
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A10 Server-Side Request Forgery (SSRF)
- OWASP API Security Top 10 2023: API7 Server Side Request Forgery
- SANS CWE Top 25 2025: #22 CWE-918
- SANS CWE Top 25 2024: #19 CWE-918

### Objetivos

- Entender o que é SSRF: fazer o servidor da aplicação buscar uma URL escolhida por quem ataca
- Explorar a falha usando o importador para ler um serviço interno que o usuário não deveria alcançar
- Entender por que "é só uma busca de documento" vira acesso à infraestrutura interna
- Corrigir com uma lista de permissão (allowlist) de destinos, validada no servidor

### Etapas

1. Conhecer a Mesa e achar onde o servidor busca a URL (10 pts)
2. Usar o importador para ler um serviço interno (15 pts)
3. Ver que o importador não distingue destino nenhum (15 pts)
4. Escolher a defesa certa contra SSRF (15 pts)
5. Corrigir o importador com uma lista de permissão (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (SSRF no importador por URL, Siderúrgica Pindorama; família ssrf, ramo Indústria e Energia). |

## LAB-023 · A8-FIN · Lógica de negócio: o resgate que aceita qualquer valor

- Versão vigente: 1.0.0
- Cenário: autoatendimento de Resgate de Investimento, onde o cooperado resgata parte do saldo investido para a conta corrente
- Papel do aluno: Pessoa desenvolvedora da squad de investimentos da Cooperativa Credimova
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: logica-negocio
- Ramo: Financeiro
- Módulo do curso: Foundation

### Classificação

- CWE: CWE-840 (principal), CWE-20
- OWASP Top 10 2025: A06 Insecure Design
- OWASP Top 10 2021: A04 Insecure Design
- OWASP API Security Top 10 2023: API6 Unrestricted Access to Sensitive Business Flows
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender o que é uma falha de lógica de negócio e por que ela passa pelos testes funcionais
- Explorar a falha pedindo um resgate acima do saldo e um valor negativo
- Reconhecer que a regra de negócio precisa ser conferida no servidor, não confiada ao cliente
- Corrigir aplicando as regras (valor positivo e dentro do saldo) na camada de serviço

### Etapas

1. Conhecer o resgate e achar a regra de negócio (10 pts)
2. Pedir um resgate que deveria ser impossível (15 pts)
3. Nomear a regra que faltou (15 pts)
4. Decidir onde a regra tem que valer (15 pts)
5. Aplicar a regra de negócio no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (falha de lógica de negócio no resgate, Cooperativa Credimova; família logica-negocio, ramo Financeiro). |

## LAB-024 · A8-SAU · Lógica de negócio: o reembolso que aceita qualquer valor

- Versão vigente: 1.0.0
- Cenário: Portal do Beneficiário, onde o beneficiário solicita o reembolso a partir do saldo de reembolso já aprovado
- Papel do aluno: Pessoa desenvolvedora do time de produtos digitais da operadora Sereno Saúde
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: logica-negocio
- Ramo: Saúde
- Módulo do curso: Foundation

### Classificação

- CWE: CWE-840 (principal), CWE-20
- OWASP Top 10 2025: A06 Insecure Design
- OWASP Top 10 2021: A04 Insecure Design
- OWASP API Security Top 10 2023: API6 Unrestricted Access to Sensitive Business Flows
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender o que é uma falha de lógica de negócio e por que ela passa pelos testes funcionais
- Explorar a falha pedindo um resgate acima do saldo e um valor negativo
- Reconhecer que a regra de negócio precisa ser conferida no servidor, não confiada ao cliente
- Corrigir aplicando as regras (valor positivo e dentro do saldo) na camada de serviço

### Etapas

1. Conhecer o resgate e achar a regra de negócio (10 pts)
2. Pedir um resgate que deveria ser impossível (15 pts)
3. Nomear a regra que faltou (15 pts)
4. Decidir onde a regra tem que valer (15 pts)
5. Aplicar a regra de negócio no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (falha de lógica de negócio no reembolso, Sereno Saúde; família logica-negocio, ramo Saúde). |

## LAB-025 · A8-IND · Lógica de negócio: o uso de créditos que aceita qualquer valor

- Versão vigente: 1.0.0
- Cenário: Portal do Cliente, onde o cliente converte créditos de energia em desconto na fatura
- Papel do aluno: Pessoa desenvolvedora do time digital da Voltera Distribuidora de Energia
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: logica-negocio
- Ramo: Indústria e Energia
- Módulo do curso: Foundation

### Classificação

- CWE: CWE-840 (principal), CWE-20
- OWASP Top 10 2025: A06 Insecure Design
- OWASP Top 10 2021: A04 Insecure Design
- OWASP API Security Top 10 2023: API6 Unrestricted Access to Sensitive Business Flows
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender o que é uma falha de lógica de negócio e por que ela passa pelos testes funcionais
- Explorar a falha pedindo um resgate acima do saldo e um valor negativo
- Reconhecer que a regra de negócio precisa ser conferida no servidor, não confiada ao cliente
- Corrigir aplicando as regras (valor positivo e dentro do saldo) na camada de serviço

### Etapas

1. Conhecer o resgate e achar a regra de negócio (10 pts)
2. Pedir um resgate que deveria ser impossível (15 pts)
3. Nomear a regra que faltou (15 pts)
4. Decidir onde a regra tem que valer (15 pts)
5. Aplicar a regra de negócio no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (falha de lógica de negócio no uso de créditos, Voltera Distribuidora de Energia; família logica-negocio, ramo Indústria e Energia). |

## LAB-026 · A13-FIN · Força bruta no login: o login que aceita senhas sem parar

- Versão vigente: 1.0.0
- Cenário: Área do Cliente, onde o cliente entra com usuário e senha para acessar a própria conta
- Papel do aluno: Pessoa desenvolvedora do time de contas da fintech Pagomais
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: tentativas-login
- Ramo: Financeiro
- Módulo do curso: Trained

### Classificação

- CWE: CWE-307 (principal), CWE-770
- OWASP Top 10 2025: A07 Authentication Failures
- OWASP Top 10 2021: A07 Identification and Authentication Failures
- OWASP API Security Top 10 2023: API2 Broken Authentication
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que um login sem limite de tentativas permite ataque de força bruta
- Explorar a falha enviando várias tentativas de senha seguidas, sem bloqueio
- Reconhecer que o limite precisa ser contado no servidor, por usuário
- Corrigir limitando as tentativas por usuário na camada de serviço

### Etapas

1. Conhecer o login e achar o serviço de autenticação (10 pts)
2. Testar várias senhas seguidas, sem bloqueio (15 pts)
3. Nomear a defesa que falta (15 pts)
4. Decidir onde o limite tem que valer (15 pts)
5. Limitar as tentativas no serviço de autenticação (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (login sem limite de tentativas / força bruta, Pagomais; família tentativas-login, ramo Financeiro). |

## LAB-027 · A13-SAU · Força bruta no login: o login que aceita senhas sem parar

- Versão vigente: 1.0.0
- Cenário: Portal do Paciente, onde o paciente entra com usuário e senha para acessar os próprios dados
- Papel do aluno: Pessoa desenvolvedora do time de produtos digitais da Clínica Lumen
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: tentativas-login
- Ramo: Saúde
- Módulo do curso: Trained

### Classificação

- CWE: CWE-307 (principal), CWE-770
- OWASP Top 10 2025: A07 Authentication Failures
- OWASP Top 10 2021: A07 Identification and Authentication Failures
- OWASP API Security Top 10 2023: API2 Broken Authentication
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que um login sem limite de tentativas permite ataque de força bruta
- Explorar a falha enviando várias tentativas de senha seguidas, sem bloqueio
- Reconhecer que o limite precisa ser contado no servidor, por usuário
- Corrigir limitando as tentativas por usuário na camada de serviço

### Etapas

1. Conhecer o login e achar o serviço de autenticação (10 pts)
2. Testar várias senhas seguidas, sem bloqueio (15 pts)
3. Nomear a defesa que falta (15 pts)
4. Decidir onde o limite tem que valer (15 pts)
5. Limitar as tentativas no serviço de autenticação (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (login sem limite de tentativas / força bruta, Clínica Lumen; família tentativas-login, ramo Saúde). |

## LAB-028 · A13-IND · Força bruta no login: o login que aceita senhas sem parar

- Versão vigente: 1.0.0
- Cenário: Portal do Fornecedor, onde o fornecedor entra com usuário e senha para acessar pedidos e notas
- Papel do aluno: Pessoa desenvolvedora do time digital da Metalúrgica Aurora
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: tentativas-login
- Ramo: Indústria e Energia
- Módulo do curso: Trained

### Classificação

- CWE: CWE-307 (principal), CWE-770
- OWASP Top 10 2025: A07 Authentication Failures
- OWASP Top 10 2021: A07 Identification and Authentication Failures
- OWASP API Security Top 10 2023: API2 Broken Authentication
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que um login sem limite de tentativas permite ataque de força bruta
- Explorar a falha enviando várias tentativas de senha seguidas, sem bloqueio
- Reconhecer que o limite precisa ser contado no servidor, por usuário
- Corrigir limitando as tentativas por usuário na camada de serviço

### Etapas

1. Conhecer o login e achar o serviço de autenticação (10 pts)
2. Testar várias senhas seguidas, sem bloqueio (15 pts)
3. Nomear a defesa que falta (15 pts)
4. Decidir onde o limite tem que valer (15 pts)
5. Limitar as tentativas no serviço de autenticação (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (login sem limite de tentativas / força bruta, Metalúrgica Aurora; família tentativas-login, ramo Indústria e Energia). |

## LAB-029 · A7-FIN · CORS mal configurado: o perfil que qualquer site pode ler

- Versão vigente: 1.0.0
- Cenário: Portal do Investidor, onde o investidor vê o próprio perfil carregado pela API da plataforma
- Papel do aluno: Pessoa desenvolvedora do time de plataforma da Corretora Montara
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: cors
- Ramo: Financeiro
- Módulo do curso: Trained

### Classificação

- CWE: CWE-942 (principal), CWE-346
- OWASP Top 10 2025: A02 Security Misconfiguration
- OWASP Top 10 2021: A05 Security Misconfiguration
- OWASP API Security Top 10 2023: API8 Security Misconfiguration
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender o que o CORS controla e o que o cabeçalho Access-Control-Allow-Origin libera
- Explorar a falha vendo a API refletir qualquer origem enviada na requisição
- Reconhecer o risco de refletir a origem junto com Allow-Credentials
- Corrigir liberando só origens confiáveis, de uma lista conhecida

### Etapas

1. Conhecer a API e achar a configuração de CORS (10 pts)
2. Ver a API refletir qualquer origem (15 pts)
3. Nomear a defesa que falta (15 pts)
4. Entender o papel das credenciais (15 pts)
5. Liberar só origens confiáveis no serviço de CORS (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (CORS mal configurado que reflete qualquer origem, Corretora Montara; família cors, ramo Financeiro). |

## LAB-030 · A7-SAU · CORS mal configurado: o perfil que qualquer site pode ler

- Versão vigente: 1.0.0
- Cenário: Portal do Beneficiário, onde o beneficiário vê o próprio perfil carregado pela API da operadora
- Papel do aluno: Pessoa desenvolvedora do time de produtos digitais da operadora Vitalis
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: cors
- Ramo: Saúde
- Módulo do curso: Trained

### Classificação

- CWE: CWE-942 (principal), CWE-346
- OWASP Top 10 2025: A02 Security Misconfiguration
- OWASP Top 10 2021: A05 Security Misconfiguration
- OWASP API Security Top 10 2023: API8 Security Misconfiguration
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender o que o CORS controla e o que o cabeçalho Access-Control-Allow-Origin libera
- Explorar a falha vendo a API refletir qualquer origem enviada na requisição
- Reconhecer o risco de refletir a origem junto com Allow-Credentials
- Corrigir liberando só origens confiáveis, de uma lista conhecida

### Etapas

1. Conhecer a API e achar a configuração de CORS (10 pts)
2. Ver a API refletir qualquer origem (15 pts)
3. Nomear a defesa que falta (15 pts)
4. Entender o papel das credenciais (15 pts)
5. Liberar só origens confiáveis no serviço de CORS (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (CORS mal configurado que reflete qualquer origem, Operadora Vitalis; família cors, ramo Saúde). |

## LAB-031 · A7-IND · CORS mal configurado: o perfil que qualquer site pode ler

- Versão vigente: 1.0.0
- Cenário: Portal do Cliente, onde o cliente vê o próprio perfil carregado pela API da distribuidora
- Papel do aluno: Pessoa desenvolvedora do time digital da Corrente Energia
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: cors
- Ramo: Indústria e Energia
- Módulo do curso: Trained

### Classificação

- CWE: CWE-942 (principal), CWE-346
- OWASP Top 10 2025: A02 Security Misconfiguration
- OWASP Top 10 2021: A05 Security Misconfiguration
- OWASP API Security Top 10 2023: API8 Security Misconfiguration
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender o que o CORS controla e o que o cabeçalho Access-Control-Allow-Origin libera
- Explorar a falha vendo a API refletir qualquer origem enviada na requisição
- Reconhecer o risco de refletir a origem junto com Allow-Credentials
- Corrigir liberando só origens confiáveis, de uma lista conhecida

### Etapas

1. Conhecer a API e achar a configuração de CORS (10 pts)
2. Ver a API refletir qualquer origem (15 pts)
3. Nomear a defesa que falta (15 pts)
4. Entender o papel das credenciais (15 pts)
5. Liberar só origens confiáveis no serviço de CORS (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (CORS mal configurado que reflete qualquer origem, Corrente Energia; família cors, ramo Indústria e Energia). |

## LAB-032 · A12-FIN · Path traversal: o documento que foge da pasta

- Versão vigente: 1.0.0
- Cenário: Central de Documentos, onde o investidor baixa os próprios documentos pelo nome
- Papel do aluno: Pessoa desenvolvedora do time de plataforma da Corretora Montara
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: path-traversal
- Ramo: Financeiro
- Módulo do curso: Trained

### Classificação

- CWE: CWE-22 (principal), CWE-23, CWE-36
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- OWASP API Security Top 10 2023: API1 Broken Object Level Authorization
- SANS CWE Top 25 2025: #6 CWE-22 Path Traversal
- SANS CWE Top 25 2024: #5 CWE-22 Path Traversal

### Objetivos

- Entender o que é path traversal e como um nome de arquivo sai da pasta permitida
- Explorar a falha baixando um arquivo fora da pasta de documentos com ../
- Reconhecer que validar o nome por string (bloquear "..") não basta
- Corrigir garantindo que o caminho final fique dentro da pasta de documentos

### Etapas

1. Conhecer o download e achar a leitura do arquivo (10 pts)
2. Baixar um arquivo fora da pasta de documentos (15 pts)
3. Entender por que bloquear ".." não basta (15 pts)
4. Nomear a regra que vale (15 pts)
5. Garantir o caminho dentro da pasta no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (path traversal no download de documentos, Corretora Montara; família path-traversal, ramo Financeiro). |

## LAB-033 · A12-SAU · Path traversal: o documento que foge da pasta

- Versão vigente: 1.0.0
- Cenário: Central de Documentos, onde o beneficiário baixa os próprios documentos pelo nome
- Papel do aluno: Pessoa desenvolvedora do time de produtos digitais da operadora Vitalis
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: path-traversal
- Ramo: Saúde
- Módulo do curso: Trained

### Classificação

- CWE: CWE-22 (principal), CWE-23, CWE-36
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- OWASP API Security Top 10 2023: API1 Broken Object Level Authorization
- SANS CWE Top 25 2025: #6 CWE-22 Path Traversal
- SANS CWE Top 25 2024: #5 CWE-22 Path Traversal

### Objetivos

- Entender o que é path traversal e como um nome de arquivo sai da pasta permitida
- Explorar a falha baixando um arquivo fora da pasta de documentos com ../
- Reconhecer que validar o nome por string (bloquear "..") não basta
- Corrigir garantindo que o caminho final fique dentro da pasta de documentos

### Etapas

1. Conhecer o download e achar a leitura do arquivo (10 pts)
2. Baixar um arquivo fora da pasta de documentos (15 pts)
3. Entender por que bloquear ".." não basta (15 pts)
4. Nomear a regra que vale (15 pts)
5. Garantir o caminho dentro da pasta no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (path traversal no download de documentos, Operadora Vitalis; família path-traversal, ramo Saúde). |

## LAB-034 · A12-IND · Path traversal: o documento que foge da pasta

- Versão vigente: 1.0.0
- Cenário: Central de Documentos, onde o cliente baixa os próprios documentos pelo nome
- Papel do aluno: Pessoa desenvolvedora do time digital da Corrente Energia
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: path-traversal
- Ramo: Indústria e Energia
- Módulo do curso: Trained

### Classificação

- CWE: CWE-22 (principal), CWE-23, CWE-36
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- OWASP API Security Top 10 2023: API1 Broken Object Level Authorization
- SANS CWE Top 25 2025: #6 CWE-22 Path Traversal
- SANS CWE Top 25 2024: #5 CWE-22 Path Traversal

### Objetivos

- Entender o que é path traversal e como um nome de arquivo sai da pasta permitida
- Explorar a falha baixando um arquivo fora da pasta de documentos com ../
- Reconhecer que validar o nome por string (bloquear "..") não basta
- Corrigir garantindo que o caminho final fique dentro da pasta de documentos

### Etapas

1. Conhecer o download e achar a leitura do arquivo (10 pts)
2. Baixar um arquivo fora da pasta de documentos (15 pts)
3. Entender por que bloquear ".." não basta (15 pts)
4. Nomear a regra que vale (15 pts)
5. Garantir o caminho dentro da pasta no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (path traversal no download de documentos, Corrente Energia; família path-traversal, ramo Indústria e Energia). |

## LAB-035 · A10-FIN · Confiança no cliente: a loja que confia no preço do cliente

- Versão vigente: 1.0.0
- Cenário: Clube de Pontos, onde o cooperado resgata produtos gastando pontos do programa de fidelidade
- Papel do aluno: Pessoa desenvolvedora da squad de engajamento da Cooperativa Credimova
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: confianca-cliente
- Ramo: Financeiro
- Módulo do curso: Trained

### Classificação

- CWE: CWE-602 (principal), CWE-472
- OWASP Top 10 2025: A06 Insecure Design
- OWASP Top 10 2021: A04 Insecure Design
- OWASP API Security Top 10 2023: API6 Unrestricted Access to Sensitive Business Flows
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que não se deve confiar em dados que o cliente controla
- Explorar a falha resgatando um produto caro com um custo adulterado no pedido
- Reconhecer que o custo do produto é um dado do servidor, não do formulário
- Corrigir usando o custo real do produto (do banco) e ignorando o do formulário

### Etapas

1. Conhecer a loja e achar o resgate (10 pts)
2. Resgatar um produto caro pagando 1 ponto (15 pts)
3. Dizer de onde o custo deve vir (15 pts)
4. Decidir se o servidor pode confiar no formulário (15 pts)
5. Usar o custo real do produto no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (loja confia no custo enviado pelo cliente, Cooperativa Credimova; família confianca-cliente, ramo Financeiro). |

## LAB-036 · A10-SAU · Confiança no cliente: a loja que confia no preço do cliente

- Versão vigente: 1.0.0
- Cenário: Clube de Bem-Estar, onde o beneficiário resgata produtos gastando pontos do programa de saúde
- Papel do aluno: Pessoa desenvolvedora do time de produtos digitais da operadora Sereno Saúde
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: confianca-cliente
- Ramo: Saúde
- Módulo do curso: Trained

### Classificação

- CWE: CWE-602 (principal), CWE-472
- OWASP Top 10 2025: A06 Insecure Design
- OWASP Top 10 2021: A04 Insecure Design
- OWASP API Security Top 10 2023: API6 Unrestricted Access to Sensitive Business Flows
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que não se deve confiar em dados que o cliente controla
- Explorar a falha resgatando um produto caro com um custo adulterado no pedido
- Reconhecer que o custo do produto é um dado do servidor, não do formulário
- Corrigir usando o custo real do produto (do banco) e ignorando o do formulário

### Etapas

1. Conhecer a loja e achar o resgate (10 pts)
2. Resgatar um produto caro pagando 1 ponto (15 pts)
3. Dizer de onde o custo deve vir (15 pts)
4. Decidir se o servidor pode confiar no formulário (15 pts)
5. Usar o custo real do produto no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (loja confia no custo enviado pelo cliente, Sereno Saúde; família confianca-cliente, ramo Saúde). |

## LAB-037 · A10-IND · Confiança no cliente: a loja que confia no preço do cliente

- Versão vigente: 1.0.0
- Cenário: Clube de Vantagens, onde o cliente resgata produtos gastando pontos do programa de relacionamento
- Papel do aluno: Pessoa desenvolvedora do time digital da Voltera Distribuidora de Energia
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: confianca-cliente
- Ramo: Indústria e Energia
- Módulo do curso: Trained

### Classificação

- CWE: CWE-602 (principal), CWE-472
- OWASP Top 10 2025: A06 Insecure Design
- OWASP Top 10 2021: A04 Insecure Design
- OWASP API Security Top 10 2023: API6 Unrestricted Access to Sensitive Business Flows
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que não se deve confiar em dados que o cliente controla
- Explorar a falha resgatando um produto caro com um custo adulterado no pedido
- Reconhecer que o custo do produto é um dado do servidor, não do formulário
- Corrigir usando o custo real do produto (do banco) e ignorando o do formulário

### Etapas

1. Conhecer a loja e achar o resgate (10 pts)
2. Resgatar um produto caro pagando 1 ponto (15 pts)
3. Dizer de onde o custo deve vir (15 pts)
4. Decidir se o servidor pode confiar no formulário (15 pts)
5. Usar o custo real do produto no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (loja confia no custo enviado pelo cliente, Voltera Distribuidora de Energia; família confianca-cliente, ramo Indústria e Energia). |

## LAB-038 · A15-FIN · Autorização de função: a API de admin aberta para todos

- Versão vigente: 1.0.0
- Cenário: Console Interno, onde funcionários acessam, conforme o papel, as funções de atendimento e as administrativas
- Papel do aluno: Pessoa desenvolvedora do time de backoffice do Banco Lumina
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: autorizacao-api
- Ramo: Financeiro
- Módulo do curso: Trained

### Classificação

- CWE: CWE-862 (principal), CWE-863
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- OWASP API Security Top 10 2023: API5 Broken Function Level Authorization
- SANS CWE Top 25 2025: #4 CWE-862 Missing Authorization
- SANS CWE Top 25 2024: #9 CWE-862 Missing Authorization

### Objetivos

- Distinguir autenticação (quem é) de autorização (o que pode fazer)
- Explorar a falha chamando a API administrativa como um usuário comum
- Reconhecer que cada função sensível precisa conferir o papel do usuário
- Corrigir exigindo o papel admin antes de executar a função

### Etapas

1. Conhecer a API administrativa e os papéis (10 pts)
2. Chamar a API de admin como usuário comum (15 pts)
3. Separar autenticação de autorização (15 pts)
4. Nomear o que precisa ser conferido (15 pts)
5. Exigir o papel admin no serviço de permissão (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (API administrativa sem conferência de papel / BFLA, Banco Lumina; família autorizacao-api, ramo Financeiro). |

## LAB-039 · A15-SAU · Autorização de função: a API de admin aberta para todos

- Versão vigente: 1.0.0
- Cenário: Console Interno, onde a equipe acessa, conforme o papel, as funções de atendimento e as administrativas
- Papel do aluno: Pessoa desenvolvedora do time de sistemas do Hospital Santa Clara
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: autorizacao-api
- Ramo: Saúde
- Módulo do curso: Trained

### Classificação

- CWE: CWE-862 (principal), CWE-863
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- OWASP API Security Top 10 2023: API5 Broken Function Level Authorization
- SANS CWE Top 25 2025: #4 CWE-862 Missing Authorization
- SANS CWE Top 25 2024: #9 CWE-862 Missing Authorization

### Objetivos

- Distinguir autenticação (quem é) de autorização (o que pode fazer)
- Explorar a falha chamando a API administrativa como um usuário comum
- Reconhecer que cada função sensível precisa conferir o papel do usuário
- Corrigir exigindo o papel admin antes de executar a função

### Etapas

1. Conhecer a API administrativa e os papéis (10 pts)
2. Chamar a API de admin como usuário comum (15 pts)
3. Separar autenticação de autorização (15 pts)
4. Nomear o que precisa ser conferido (15 pts)
5. Exigir o papel admin no serviço de permissão (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (API administrativa sem conferência de papel / BFLA, Hospital Santa Clara; família autorizacao-api, ramo Saúde). |

## LAB-040 · A15-IND · Autorização de função: a API de admin aberta para todos

- Versão vigente: 1.0.0
- Cenário: Console Interno, onde a equipe acessa, conforme o papel, as funções operacionais e as administrativas
- Papel do aluno: Pessoa desenvolvedora do time digital da Petroquímica Horizonte
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 35 min
- Família: autorizacao-api
- Ramo: Indústria e Energia
- Módulo do curso: Trained

### Classificação

- CWE: CWE-862 (principal), CWE-863
- OWASP Top 10 2025: A01 Broken Access Control
- OWASP Top 10 2021: A01 Broken Access Control
- OWASP API Security Top 10 2023: API5 Broken Function Level Authorization
- SANS CWE Top 25 2025: #4 CWE-862 Missing Authorization
- SANS CWE Top 25 2024: #9 CWE-862 Missing Authorization

### Objetivos

- Distinguir autenticação (quem é) de autorização (o que pode fazer)
- Explorar a falha chamando a API administrativa como um usuário comum
- Reconhecer que cada função sensível precisa conferir o papel do usuário
- Corrigir exigindo o papel admin antes de executar a função

### Etapas

1. Conhecer a API administrativa e os papéis (10 pts)
2. Chamar a API de admin como usuário comum (15 pts)
3. Separar autenticação de autorização (15 pts)
4. Nomear o que precisa ser conferido (15 pts)
5. Exigir o papel admin no serviço de permissão (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (API administrativa sem conferência de papel / BFLA, Petroquímica Horizonte; família autorizacao-api, ramo Indústria e Energia). |

## LAB-041 · A19-FIN · Erros verbosos: a API que mostra o traceback

- Versão vigente: 1.0.0
- Cenário: Painel de Relatórios, onde o analista gera relatórios mensais por uma API interna
- Papel do aluno: Pessoa desenvolvedora do time de dados da Fintech Nimbo
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 30 min
- Família: erros-verbosos
- Ramo: Financeiro
- Módulo do curso: Trained

### Classificação

- CWE: CWE-209 (principal), CWE-755
- OWASP Top 10 2025: A10 Mishandling of Exceptional Conditions
- OWASP Top 10 2021: A05 Security Misconfiguration
- OWASP API Security Top 10 2023: API8 Security Misconfiguration
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que mensagens de erro detalhadas vazam informação útil ao atacante
- Explorar a falha forçando um erro e lendo o traceback na resposta
- Reconhecer que o detalhe do erro deve ir para o log, não para o cliente
- Corrigir devolvendo uma mensagem genérica e registrando o detalhe no servidor

### Etapas

1. Conhecer a API de relatório e o tratamento de erro (10 pts)
2. Forçar um erro e ler o traceback na resposta (15 pts)
3. Decidir para onde o detalhe deve ir (15 pts)
4. Decidir o que o cliente deve receber (15 pts)
5. Registrar o detalhe e responder genérico no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (erros verbosos / traceback na resposta da API, Fintech Nimbo; família erros-verbosos, ramo Financeiro). |

## LAB-042 · A19-SAU · Erros verbosos: a API que mostra o traceback

- Versão vigente: 1.0.0
- Cenário: Painel de Relatórios, onde a equipe gera relatórios mensais por uma API interna
- Papel do aluno: Pessoa desenvolvedora do time de dados da operadora Prisma
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 30 min
- Família: erros-verbosos
- Ramo: Saúde
- Módulo do curso: Trained

### Classificação

- CWE: CWE-209 (principal), CWE-755
- OWASP Top 10 2025: A10 Mishandling of Exceptional Conditions
- OWASP Top 10 2021: A05 Security Misconfiguration
- OWASP API Security Top 10 2023: API8 Security Misconfiguration
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que mensagens de erro detalhadas vazam informação útil ao atacante
- Explorar a falha forçando um erro e lendo o traceback na resposta
- Reconhecer que o detalhe do erro deve ir para o log, não para o cliente
- Corrigir devolvendo uma mensagem genérica e registrando o detalhe no servidor

### Etapas

1. Conhecer a API de relatório e o tratamento de erro (10 pts)
2. Forçar um erro e ler o traceback na resposta (15 pts)
3. Decidir para onde o detalhe deve ir (15 pts)
4. Decidir o que o cliente deve receber (15 pts)
5. Registrar o detalhe e responder genérico no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (erros verbosos / traceback na resposta da API, Operadora Prisma; família erros-verbosos, ramo Saúde). |

## LAB-043 · A19-IND · Erros verbosos: a API que mostra o traceback

- Versão vigente: 1.0.0
- Cenário: Painel de Relatórios, onde a equipe gera relatórios mensais de produção por uma API interna
- Papel do aluno: Pessoa desenvolvedora do time digital da Metalúrgica Delta
- Linguagem / stack: python / flask
- Nível: Intermediário · duração estimada: 30 min
- Família: erros-verbosos
- Ramo: Indústria e Energia
- Módulo do curso: Trained

### Classificação

- CWE: CWE-209 (principal), CWE-755
- OWASP Top 10 2025: A10 Mishandling of Exceptional Conditions
- OWASP Top 10 2021: A05 Security Misconfiguration
- OWASP API Security Top 10 2023: API8 Security Misconfiguration
- SANS CWE Top 25 2025: Não se enquadra; use o CWE
- SANS CWE Top 25 2024: Não se enquadra; use o CWE

### Objetivos

- Entender por que mensagens de erro detalhadas vazam informação útil ao atacante
- Explorar a falha forçando um erro e lendo o traceback na resposta
- Reconhecer que o detalhe do erro deve ir para o log, não para o cliente
- Corrigir devolvendo uma mensagem genérica e registrando o detalhe no servidor

### Etapas

1. Conhecer a API de relatório e o tratamento de erro (10 pts)
2. Forçar um erro e ler o traceback na resposta (15 pts)
3. Decidir para onde o detalhe deve ir (15 pts)
4. Decidir o que o cliente deve receber (15 pts)
5. Registrar o detalhe e responder genérico no serviço (45 pts)

### Histórico de versões

| Versão | Criada em | Obsoleta em | Situação | O que mudou |
|---|---|---|---|---|
| 1.0.0 | 2026-11-17 | — | vigente | Primeira versão (erros verbosos / traceback na resposta da API, Metalúrgica Delta; família erros-verbosos, ramo Indústria e Energia). |
