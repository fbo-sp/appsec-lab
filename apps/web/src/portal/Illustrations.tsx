import type { ReactNode } from "react";

/**
 * Ilustrações fixas da interface para o texto das etapas (ADR-018, extensão do ADR-012).
 *
 * No Markdown restrito, um bloco cercado com a linguagem `ilustracao` e um nome conhecido vira um
 * desenho da própria tela, feito só com elementos React e CSS: nada vem de fora nem do manifesto além
 * do nome. Nome desconhecido continua aparecendo como bloco de código.
 */
type Tone = "atk" | "app" | "vit" | "bad" | "ok";

/** Fluxo vertical (o painel da etapa é estreito): quem faz o quê, com setas entre os passos. */
function Flow({ steps }: { steps: { who: string; what: ReactNode; tone: Tone }[] }) {
  return (
    <ol className="ill-flow">
      {steps.map((st, i) => (
        <li key={i} className={`ill-node ill-${st.tone}`}>
          <b>{st.who}</b>
          <span>{st.what}</span>
        </li>
      ))}
    </ol>
  );
}

/** Antes e depois lado a lado: o código vulnerável e o corrigido. */
function Compare({ bad, good }: { bad: [string, ReactNode]; good: [string, ReactNode] }) {
  return (
    <div className="ill-compare">
      <div className="ill-node ill-bad">
        <b>✗ {bad[0]}</b>
        {bad[1]}
      </div>
      <div className="ill-node ill-ok">
        <b>✓ {good[0]}</b>
        {good[1]}
      </div>
    </div>
  );
}

const c = (t: string) => <code className="ill-mono">{t}</code>;

const ILLUSTRATIONS: Record<string, { caption: string; body: () => ReactNode }> = {
  tela: {
    caption: "As duas áreas da tela: o painel da etapa à esquerda e o ambiente com as abas à direita.",
    body: () => (
      <div className="ill-screen">
        <div className="ill-side">
          <div className="ill-score">
            10 / 100 pts <span className="ill-trail"><i className="on" /><i /><i /><i /><i /></span>
          </div>
          <div className="ill-lines">
            <b>Etapa 1</b>
            <span />
            <span />
            <span className="short" />
          </div>
          <div className="ill-row">
            <span className="ill-input" />
            <span className="ill-btn">Validar</span>
          </div>
        </div>
        <div className="ill-main">
          <div className="ill-tabs">
            <span className="on">Aplicação</span>
            <span>Código</span>
            <span>Terminal</span>
            <span>Validação</span>
          </div>
          <div className="ill-page">
            <span className="ill-box">Código da etapa 1: ●●●●</span>
          </div>
        </div>
      </div>
    ),
  },
  "barra-endereco": {
    caption: "A barra de endereço fica no topo da aba Aplicação. Digite o caminho e pressione Enter.",
    body: () => (
      <div className="ill-toolbar">
        <span className="ill-field ill-focus">/tutorial/endereco.html</span>
        <span className="ill-link">ir</span>
        <span className="ill-info">i</span>
        <span className="ill-link">recarregar</span>
        <span className="ill-link">abrir em nova aba</span>
      </div>
    ),
  },
  terminal: {
    caption: "Clique na área escura, digite o comando e pressione Enter. A resposta aparece na linha de baixo.",
    body: () => (
      <div className="ill-terminal">
        <div>
          <span className="ill-prompt">aluno@lab:/workspace$</span> whoami<span className="ill-caret" />
        </div>
        <div className="ill-out">← o nome do usuário aparece aqui</div>
      </div>
    ),
  },
  dicas: {
    caption: "O botão Dicas fica ao lado de Validar. Cada dica mostra o custo antes de ser aberta.",
    body: () => (
      <div className="ill-hints">
        <div className="ill-row">
          <span className="ill-input" />
          <span className="ill-btn">Validar</span>
          <span className="ill-btn ill-ghost ill-focus">Dicas (0/3)</span>
        </div>
        <ul>
          <li>
            Dica 1 <em className="free">grátis</em>
          </li>
          <li>
            Dica 2 <em>−1 ponto</em>
          </li>
          <li>
            Dica 3 <em>−2 pontos</em>
          </li>
        </ul>
      </div>
    ),
  },
  "editar-validar": {
    caption: "Abra o arquivo na aba Código, edite, salve com Ctrl+S e clique em Validar.",
    body: () => (
      <div className="ill-editor">
        <div className="ill-files">
          <span className="on">index.html</span>
          <span>README.md</span>
          <span>tutorial/</span>
        </div>
        <pre className="ill-code">
          <span>{"<h1>Boas-vindas…</h1>"}</span>
          <span className="ill-added">{"<p>Olá, CECyber</p>"}</span>
          <span>{"<p>Esta é a aplicação…</p>"}</span>
        </pre>
        <div className="ill-result">✓ Aprovado na validação</div>
      </div>
    ),
  },
  // Diagramas conceituais dos laboratórios (genéricos: servem a todos os ramos de uma família).
  "xss-lista-bloqueio": {
    caption: "Uma lista de bloqueio só pega o formato que o time imaginou. Outras tags com eventos passam.",
    body: () => (
      <div className="ill-table">
        <div className="ill-node ill-app">
          <b>limpar_texto remove só {"<script>"}</b>
        </div>
        <ul>
          <li className="ill-blocked">{c("<script>alert(1)</script>")} bloqueado</li>
          <li className="ill-passed">{c("<b>negrito</b>")} passa</li>
          <li className="ill-passed">{c("<img src=x onerror=…>")} passa</li>
          <li className="ill-passed">{c("<svg onload=…>")} passa</li>
          <li className="ill-passed">{c("<details open ontoggle=…>")} passa</li>
        </ul>
      </div>
    ),
  },
  "xss-refletido": {
    caption: "XSS refletido: o código vai no próprio link e volta na resposta para quem abrir esse link.",
    body: () => (
      <Flow
        steps={[
          { who: "Atacante", what: <>monta um link com código na busca: {c("?q=<img src=x onerror=…>")}</>, tone: "atk" },
          { who: "Vítima", what: "clica no link recebido por e-mail ou mensagem, já logada na aplicação", tone: "vit" },
          { who: "Aplicação", what: <>repete o termo na página sem codificar: {c("{{ termo|safe }}")}</>, tone: "app" },
          { who: "Navegador da vítima", what: <>cria a tag {c("<img>")}, a imagem falha e o {c("onerror")} roda</>, tone: "vit" },
          { who: "Resultado", what: "o JavaScript lê os cookies sem HttpOnly e poderia enviá-los ao atacante", tone: "bad" },
        ]}
      />
    ),
  },
  "xss-armazenado": {
    caption: "XSS armazenado: o código fica no banco e roda para cada pessoa que abre a tela, sem precisar de link.",
    body: () => (
      <Flow
        steps={[
          { who: "Usuário comum", what: "cadastra um registro com código no campo livre", tone: "atk" },
          { who: "Banco de dados", what: "guarda o texto exatamente como chegou", tone: "app" },
          { who: "Equipe interna", what: <>abre o painel; o template imprime o campo com {c("|safe")}</>, tone: "vit" },
          { who: "Resultado", what: "o código roda no navegador da equipe, com o acesso e os cookies dela", tone: "bad" },
        ]}
      />
    ),
  },
  "xss-codificacao-saida": {
    caption: "Codificar a saída: o mesmo texto vira tag com |safe e vira texto sem ele.",
    body: () => (
      <Compare
        bad={[
          "Com |safe",
          <>
            {c("{{ termo|safe }}")}
            <span>HTML enviado: {c("<img src=x onerror=…>")}</span>
            <span>O navegador cria a tag e executa o código.</span>
          </>,
        ]}
        good={[
          "Autoescape do Jinja2",
          <>
            {c("{{ termo }}")}
            <span>HTML enviado: {c("&lt;img src=x onerror=…&gt;")}</span>
            <span>O navegador mostra o texto, sem executar.</span>
          </>,
        ]}
      />
    ),
  },
  "mass-assignment": {
    caption: "Atribuição em massa: o servidor grava todo campo que chega, inclusive os que a tela não oferece.",
    body: () => (
      <Flow
        steps={[
          { who: "Usuário", what: <>{c("PATCH /api/perfil")} com {c('{"telefone": "…", "perfil": "…"}')}</>, tone: "atk" },
          { who: "Serviço", what: <>valida o telefone e repassa o dicionário inteiro: {c("atualizar(id, dados)")}</>, tone: "app" },
          { who: "Repositório", what: <>{c("UPDATE usuarios SET telefone = ?, perfil = ?")}</>, tone: "app" },
          { who: "Resultado", what: "o próprio usuário alterou um campo que só a empresa deveria mudar", tone: "bad" },
        ]}
      />
    ),
  },
  "lista-permissao-campos": {
    caption: "Lista de permissão: só os campos que a regra de negócio permite chegam ao banco; o resto é descartado.",
    body: () => (
      <Flow
        steps={[
          { who: "JSON recebido", what: c('{"email": …, "telefone": …, "perfil": …, "login": …}'), tone: "atk" },
          { who: "Serviço", what: <>{c('CAMPOS_EDITAVEIS = ("email", "telefone")')} filtra o dicionário</>, tone: "app" },
          { who: "Repositório", what: <>{c("UPDATE usuarios SET email = ?, telefone = ?")}</>, tone: "ok" },
          { who: "Descartados", what: <>{c("perfil")}, {c("login")} e qualquer coluna criada no futuro</>, tone: "ok" },
        ]}
      />
    ),
  },
  "site-vs-origem": {
    caption: "Origem é esquema + endereço + porta. Site é o domínio registrável. SameSite olha o site.",
    body: () => (
      <div className="ill-table">
        <div className="ill-node ill-app">
          <b>Mesmo site: empresa.example</b>
          <span>
            {c("https://portal.empresa.example")} e {c("https://campanhas.empresa.example")}
          </span>
          <span>origens diferentes, mesmo site: o cookie SameSite=Lax vai junto</span>
        </div>
        <div className="ill-node ill-ok">
          <b>Outro site</b>
          <span>
            {c("https://portal.empresa.example")} e {c("https://golpe.example")}
          </span>
          <span>sites diferentes: com SameSite=Lax o cookie não vai no POST</span>
        </div>
      </div>
    ),
  },
  "csrf-fluxo": {
    caption: "CSRF: a página do atacante faz o navegador da vítima enviar o pedido, e o cookie vai junto sozinho.",
    body: () => (
      <Flow
        steps={[
          { who: "Vítima", what: "está logada na aplicação; o navegador guarda o cookie de sessão", tone: "vit" },
          { who: "Página do atacante", what: <>formulário escondido com o campo já preenchido e {c("form.submit()")}</>, tone: "atk" },
          { who: "Navegador da vítima", what: <>envia o {c("POST")} e anexa o cookie de sessão (mesmo site)</>, tone: "vit" },
          { who: "Aplicação", what: "vê um usuário logado e aceita a alteração", tone: "app" },
          { who: "Resultado", what: "o dado muda em nome da vítima, sem ela clicar em Salvar", tone: "bad" },
        ]}
      />
    ),
  },
  "csrf-token": {
    caption: "Token anti-CSRF: só a página da própria aplicação conhece o valor da sessão.",
    body: () => (
      <Compare
        bad={[
          "Página do atacante",
          <>
            <span>POST sem {c("csrf_token")} (não consegue ler o HTML da aplicação)</span>
            <span>Aplicação compara com a sessão: diferente, responde 400.</span>
          </>,
        ]}
        good={[
          "Formulário da aplicação",
          <>
            <span>{c('<input type="hidden" name="csrf_token" value="a9F…">')}</span>
            <span>Valor igual ao da sessão: alteração aceita.</span>
          </>,
        ]}
      />
    ),
  },
  "upload-tipo-informado": {
    caption: "Upload irrestrito: o servidor confere o rótulo que o cliente escreveu, e o arquivo vira uma página da aplicação.",
    body: () => (
      <Flow
        steps={[
          { who: "Atacante", what: <>envia {c("comprovante.html")} dizendo {c("Content-Type: image/png")}</>, tone: "atk" },
          { who: "Aplicação", what: <>confere só o rótulo, que está na lista, e grava o nome original</>, tone: "app" },
          { who: "Equipe interna", what: <>abre o anexo em {c("/anexos/comprovante.html")}</>, tone: "vit" },
          { who: "Navegador", what: "recebe text/html da própria aplicação e roda o script do arquivo", tone: "vit" },
          { who: "Resultado", what: "o script lê o que a sessão da equipe vê, como os cookies sem HttpOnly", tone: "bad" },
        ]}
      />
    ),
  },
  "assinatura-arquivo": {
    caption: "Rótulo × conteúdo: o tipo que vale é o dos primeiros bytes do arquivo, não o que o cliente declarou.",
    body: () => (
      <Compare
        bad={[
          "Confiar no rótulo",
          <>
            <span>{c("arquivo.mimetype")} vem do cliente: o curl escreve o que quiser.</span>
            <span>{c("comprovante.html")} gravado com o nome original vira página HTML.</span>
          </>,
        ]}
        good={[
          "Conferir a assinatura",
          <>
            <span>
              PDF começa com {c("%PDF-")}, PNG com {c("89 50 4E 47")}, JPEG com {c("FF D8 FF")}.
            </span>
            <span>
              Nome novo ({c("uuid4().hex + \".pdf\"")}) e {c("X-Content-Type-Options: nosniff")}.
            </span>
          </>,
        ]}
      />
    ),
  },
  "senha-resumo": {
    caption: "A senha nunca é guardada como texto: o sistema guarda e compara um resumo (hash).",
    body: () => (
      <Flow
        steps={[
          { who: "Usuário", what: "digita a senha no login", tone: "vit" },
          { who: "Aplicação", what: <>calcula o resumo da senha digitada ({c("resumo = hash(senha)")})</>, tone: "app" },
          { who: "Banco", what: <>guarda só o resumo, nunca a senha; o login compara resumo com resumo</>, tone: "app" },
          { who: "Observação", what: "o resumo certo depende de COMO ele é calculado — é aí que está a falha", tone: "bad" },
        ]}
      />
    ),
  },
  "senha-sem-sal": {
    caption: "MD5 sem sal × hash forte: o que muda quando duas pessoas usam a mesma senha.",
    body: () => (
      <Compare
        bad={[
          "MD5 sem sal (rápido)",
          <>
            <span>Mesma senha → mesmo resumo: dá para agrupar contas iguais.</span>
            <span>Rápido e sem sal: uma tabela pronta reverte senhas comuns na hora.</span>
          </>,
        ]}
        good={[
          "Hash forte (com sal e custo)",
          <>
            <span>Sal único por senha: mesma senha → resumos diferentes.</span>
            <span>Custo alto por tentativa: a força bruta fica cara e a tabela pronta não serve.</span>
          </>,
        ]}
      />
    ),
  },
  "senha-migracao": {
    caption: "Migração no login: a conta legada passa ao formato forte na próxima vez que o usuário entra.",
    body: () => (
      <Flow
        steps={[
          { who: "Usuário legado", what: "entra com a senha; a conta ainda está em MD5", tone: "vit" },
          { who: "Aplicação", what: <>confere o resumo antigo uma última vez; se bate, chama {c("generate_password_hash")}</>, tone: "app" },
          { who: "Banco", what: <>regrava a senha no formato forte ({c("scrypt:…")})</>, tone: "app" },
          { who: "Próximo login", what: <>já confere pelo formato forte com {c("check_password_hash")}</>, tone: "ok" },
        ]}
      />
    ),
  },
};

export function hasIllustration(name: string): boolean {
  return Object.hasOwn(ILLUSTRATIONS, name);
}

export function Illustration({ name }: { name: string }) {
  const ill = ILLUSTRATIONS[name];
  if (!ill) return null;
  return (
    <figure className="ill">
      <div aria-hidden="true">{ill.body()}</div>
      <figcaption>{ill.caption}</figcaption>
    </figure>
  );
}
