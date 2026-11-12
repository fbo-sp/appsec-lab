# ADR-009: Gateway de workspace e interface web para o ambiente local

- **Status:** Proposto, implementado só para local/test (2026-11-12). Decorre da diretriz do PO de chegar a uma interface visual testável. Revisar antes do piloto.
- **Data:** 2026-11-12
- **Relacionados:** ADR-008 (runtime Docker local), `13 §2` (gateway-ticket), `07` TM-01/TM-03/TM-13, `21` (experiência), IMP-302–304

## Contexto

O aluno precisa de editor, terminal e pré-visualização da aplicação da sessão. `13 §2` exige tickets efêmeros, escopados e não registrados em log, e proíbe entregar ao navegador URLs internas dos laboratórios. As aplicações do MVP serão **intencionalmente vulneráveis** (XSS, SQLi etc.), portanto o conteúdo delas não pode compartilhar origem com o portal.

## Decisão

1. **Agente de workspace dentro do contêiner do lab** (`laboratories/_base/python`): processo `aiohttp` em `/opt/agent` (venv separado do Python do aluno), porta 7681, com arquivos (listar/ler/gravar, 1 MiB, confinado ao workspace) e terminal (pty) via WebSocket. Roda com o mesmo uid não-root do aluno: é tratado como **não confiável**. Só é alcançável pela rede interna da sessão.
2. **Gateway** (`app/gateway`, processo próprio) conectado pelo worker a cada rede de sessão (`DOCKER_ATTACH_CONTAINER`). Ele expõe duas origens, ambas só em 127.0.0.1:
   - **workspace** (`:8001/s/{sid}/`): página do editor e terminal e a API de arquivos;
   - **preview** (`:8002/`): a aplicação do lab servida na raiz, com a sessão escolhida por cookie.
3. **Tickets**:
   - a API emite HMAC-SHA256 por sessão, usuário e finalidade (`workspace`/`preview`), com vida de 60 s e uso único, **somente ao dono** e com a sessão em `READY`/`ACTIVE`;
   - o primeiro ticket move a sessão de `READY` para `ACTIVE`;
   - o gateway troca o ticket por um *grant* em cookie `HttpOnly; SameSite=Strict`, com caminho escopado e prazo limitado pela expiração da sessão;
   - chaves são derivadas por audiência, então um ticket não vale como grant.
4. **Revogação**: cada requisição revalida estado e dono no banco (cache de 2 s). O terminal é derrubado em até 5 s após encerramento ou expiração.
5. **CSRF a partir do preview**: o preview é *same-site* com o workspace. Por isso:
   - a API do workspace exige o cabeçalho `X-Cecyber-Workspace`, que força preflight CORS e é sempre negado;
   - o WebSocket exige `Origin` igual à origem do workspace.
6. **Sem vazamento**:
   - o grant nunca é repassado ao agente nem à aplicação;
   - tickets e grants não vão para logs (só o caminho, sem query string);
   - o preview remove `X-Frame-Options`, acrescenta `frame-ancestors` do portal preservando a CSP da aplicação, e usa `Cache-Control: no-store`.
7. **Interface** (`apps/web`, React + Vite + TypeScript):
   - o portal (`:8000`, servido pela API) cobre login de desenvolvimento, catálogo, introdução, sessão e etapas;
   - o workspace (CodeMirror 6 + xterm.js) é servido pelo gateway e embutido por iframe;
   - o preview usa iframe com `sandbox`.
   - O portal tem CSP restritiva; a identidade de desenvolvimento fica no `localStorage` da origem do portal, inacessível ao preview.

## Limitações conhecidas (bloqueiam uso fora da máquina do desenvolvedor)

- Portas diferentes no mesmo host são o mesmo *site*. O preview pode enviar requisições ao workspace (mitigado pelo item 5) e definir cookies para o host. Na produção, cada origem deve ser um domínio registrável distinto, com subdomínio por sessão.
- Os cookies de preview de sessões diferentes do mesmo navegador sobrescrevem um ao outro (um preview por vez).
- O registro de tickets usados fica em memória: há uma única instância do gateway e ele não sobrevive a reinício. Produção exigirá armazenamento compartilhado.
- HTTP sem TLS (`secure_cookies=False`) apenas porque tudo fica em 127.0.0.1.
- O agente roda como o aluno: o aluno pode derrubá-lo e perder editor e terminal na própria sessão, sem efeito sobre outras.
- Não há limite de taxa nem quota de terminal (IMP-205/IMP-207).

## Alternativas consideradas

- *Exec* via API Docker para terminal e arquivos: exigiria o socket Docker no gateway, que é exposto ao navegador. Rejeitada.
- Preview com prefixo de caminho (`/s/{sid}/app/`): quebra aplicações com caminhos absolutos e colocaria a aplicação vulnerável na mesma origem do workspace. Rejeitada.
- Monaco (citado em IMP-304): trocado por CodeMirror 6, mais leve e compatível com a CSP do workspace sem workers adicionais; troca reversível.
- ttyd/code-server prontos: dependência operacional maior e menos controle sobre a autenticação. Adiada.
