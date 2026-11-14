# ADR-015: Verificações autenticadas no probe, base Node.js e contenção do LAB-004

- **Status:** Proposto (2026-11-13); implementado para teste do PO. Só local/test, como os ADR-008 a 014.
- **Data:** 2026-11-13
- **Relacionados:** ADR-008 (runtime Docker local), ADR-009 (gateway), ADR-010 (validação por cópia isolada), ADR-012, IMP-502..504, G5

## Contexto

O PO pediu o desenvolvimento conjunto do LAB-002 (IDOR, banco digital), do LAB-003 (JWT, emissora de cartões, Node.js) e do LAB-004 (Command Injection, indústria), no padrão aprovado do LAB-001. Três necessidades técnicas surgiram:

1. Controle de acesso só se valida com **usuários autenticados**: no LAB-002, a cliente A não pode ver o comprovante do cliente B, e B continua vendo o seu. O probe do ADR-010 só fazia requisições anônimas.
2. O LAB-003 é o **primeiro lab fora do Python**, e o workspace precisa do mesmo agente de arquivos e terminal.
3. O LAB-004 executa comandos do sistema operacional por meio da falha, o que pede uma análise de contenção explícita.

## Decisão

1. **Logins na suíte HTTP (`HttpLogin`).** Uma suíte pode declarar usuários **fictícios** do laboratório. Antes das verificações, o probe abre uma sessão por usuário, com cookies separados. Se `token_field` for informado, o valor desse campo da resposta JSON vira `Authorization: Bearer`.
   - Uma verificação com `as_user` usa a sessão daquele usuário. Sem `as_user`, a verificação é anônima e não leva cookies.
   - Se o login falhar, as verificações daquele usuário falham (*fail closed*) e as demais seguem.
   - As credenciais ficam no registro protegido de suítes, no plano de controle. São dados de exercício, sem valor fora do laboratório, como o token do LAB-001.
2. **Novos campos de `HttpCheck`:**
   - `headers`, para tokens forjados pela própria suíte;
   - `json`, para corpo JSON;
   - `expect_status_in`, para aceitar mais de um status, como 403 ou 404;
   - métodos `PATCH`, `PUT` e `DELETE`.
   - O probe continua só com a biblioteca padrão, em contêiner efêmero, sem segredos de infraestrutura e sem socket.
3. **Base Node.js (`cecyber-labs/base-node:local`).** Ela é derivada da base Python, que já traz o agente de workspace em `/opt/agent` e o usuário 10001, e recebe o binário do Node.js 22 copiado da imagem oficial. Não há agente novo. As dependências do lab (Express e jsonwebtoken, com versões travadas no `package-lock.json`) ficam em `/opt/lab/node_modules`, fora do workspace: não entram no snapshot nem podem ser editadas pelo aluno.
4. **Contenção do LAB-004 (somente local).** A injeção executa comandos **dentro do contêiner da própria sessão**, com:
   - o mesmo usuário sem privilégios (10001), sem capabilities e com `no-new-privileges`;
   - limite de PIDs e rede interna da sessão sem saída (ADR-008).
   
   Ou seja, o alcance é o mesmo que o terminal do aluno já tem. Os CLPs são simulados pelo utilitário `diag-clp`, que não abre conexões, e o `scada.conf` é fictício.
   
   **O gate G5 (contenção validada) continua obrigatório antes de qualquer ambiente além do local.** Docker Compose não é tratado como isolamento suficiente para código hostil em produção (ADR-002).
5. **Barra de endereço na aba Aplicação.** O aluno digita um caminho, como `/comprovantes/10457`, e o portal navega o iframe da aplicação. O destino é normalizado para a origem do preview: um endereço de outra origem volta para `/`. Isso é necessário para o IDOR do LAB-002 e para ver JSON de APIs.
6. **`curl` nas imagens dos LAB-002 e LAB-003**, para as etapas de terminal (enumeração e chamadas de API).

## Consequências

- Suítes existentes continuam válidas, porque os campos novos são opcionais. O `suite_digest` das submissões novas muda, pois a serialização inclui os campos novos. O digest registra a versão avaliada e não é comparado com valores antigos.
- Os testes `test_lab00{2,3,4}_validation.py` provam, contra Docker real, que cada suíte:
  - reprova o código original;
  - aprova correções corretas, incluindo variantes;
  - reprova correções ingênuas: proteger só a página HTML, confiar em `?cliente_id=`, barrar só `alg: none`, ignorar a validade do token, listas de bloqueio de metacaracteres e bloquear o próprio dono.
- `test_unit_probe.py` cobre sessões por usuário, token Bearer, *fail closed* no login e status aceitos.
- **Limitações aceitas, como no LAB-001:**
  - as respostas das etapas de pergunta são fixas e podem ser compartilhadas;
  - o aluno também consegue ler os arquivos fictícios pelo terminal.
- A barra de endereço não acompanha a navegação feita por links dentro da aplicação, porque o iframe é de outra origem e não pode ser lido.
- **LAB-004 1.0.1 (2026-11-13):** no teste no Windows, o checkout com CRLF quebrou o shebang do `diag-clp`, que não tinha extensão. Isso só aparecia depois da correção sem shell. O arquivo virou `diag-clp.py` (LF garantido pelo `.gitattributes`), o `.gitattributes` passou a forçar LF em `runtime/planta/**` e nos Dockerfiles, e o Dockerfile remove `\r` como defesa.
- **LAB-002 1.0.1 e ajuda da barra de endereço (2026-11-14):** no teste do PO, a etapa 2 não deixava claro onde fica a barra de endereço e a etapa 4 não dizia onde procurar o PIX de R$ 487.900,00. A etapa 2 passou a explicar a barra e a opção "abrir em nova aba", e a etapa 4 traz o `grep` do valor e o caminho para abrir o comprovante na tela. O portal ganhou um ícone **i** ao lado da barra e também ao lado do termo **barra de endereço** em negrito no texto das etapas (ajuda contextual por termo no renderizador de Markdown, sem sintaxe nova): ele abre a aba Aplicação com uma explicação curta e destaca o campo real enquanto está aberta. Respostas e suíte de correção não mudaram.
- **Releases locais fixadas por versão (2026-11-13):** `scripts/lab-local.sh` e `.ps1` registram cada release apontando para a tag `cecyber-labs/<nome>:<versão>` e a reaproveitam se já existir, para que reconstruir a base não deixe releases imutáveis apontando para imagens removidas.
