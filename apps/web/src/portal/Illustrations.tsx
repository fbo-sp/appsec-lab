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
  "ssrf-fluxo": {
    caption: "SSRF: quem controla a URL controla para onde o SERVIDOR vai — inclusive serviços internos.",
    body: () => (
      <Flow
        steps={[
          { who: "Atacante", what: <>informa uma URL interna, ex.: {c("http://127.0.0.1:9000/infra/credenciais")}</>, tone: "atk" },
          { who: "Aplicação", what: <>o servidor abre a URL com {c("urlopen(url)")}, sem conferir o destino</>, tone: "app" },
          { who: "Console interno", what: "responde ao servidor (ele está na rede interna, o atacante não)", tone: "vit" },
          { who: "Aplicação", what: "devolve a resposta na prévia, como se fosse um documento", tone: "app" },
          { who: "Resultado", what: "o atacante lê um segredo interno pela tela de importar documento", tone: "bad" },
        ]}
      />
    ),
  },
  "ssrf-allowlist": {
    caption: "Blocklist × allowlist: listar o que é proibido sempre deixa brecha; listar o que é permitido, não.",
    body: () => (
      <Compare
        bad={[
          "Lista de proibidos (blocklist)",
          <>
            <span>Barrar {c("127.0.0.1")}, {c("169.254.169.254")}, {c("file://")}… sempre sobra um jeito.</span>
            <span>Octal, IPv6, DNS que resolve para interno, redirecionamento: tudo contorna.</span>
          </>,
        ]}
        good={[
          "Lista de permissão (allowlist)",
          <>
            <span>Só {c('("http", "127.0.0.1", 8090)')} (o Serviço de Documentos) é aceito.</span>
            <span>Qualquer outro esquema, host ou porta é recusado antes da busca.</span>
          </>,
        ]}
      />
    ),
  },
  "erros-verbosos": {
    caption: "Erro verboso: o traceback na resposta entrega ao atacante o mapa interno do sistema.",
    body: () => (
      <Compare
        bad={[
          "Devolve o traceback (hoje)",
          <>
            <span>Em erro, a API responde {c('{"erro": str(exc), "detalhe": traceback}')}.</span>
            <span>O cliente vê caminhos como {c("/workspace/...")}, módulos e a tecnologia usada.</span>
          </>,
        ]}
        good={[
          "Loga o detalhe, responde genérico",
          <>
            <span>O servidor registra a exceção no log e devolve só {c('{"erro": "Erro interno..."}')}.</span>
            <span>A equipe investiga pelo log; o atacante não ganha o mapa do sistema.</span>
          </>,
        ]}
      />
    ),
  },
  "inventario-api": {
    caption: "Inventário de API: sair da documentação não é desligar — toda versão no ar precisa de dono e data de fim.",
    body: () => (
      <Compare
        bad={[
          "v1 esquecida no ar (hoje)",
          <>
            <span>A documentação mostra só {c("/api/v2")}, mas o {c("app.py")} ainda registra a {c("/api/v1")}.</span>
            <span>A v1 busca pelo id sem conferir o dono: trocar {c("v2")} por {c("v1")} reabre o IDOR.</span>
          </>,
        ]}
        good={[
          "Inventário e aposentadoria",
          <>
            <span>Cada versão tem dono e data de fim; a v1 responde {c("410 Gone")}.</span>
            <span>Se precisar conviver, a v1 passa pelo mesmo serviço que confere o dono.</span>
          </>,
        ]}
      />
    ),
  },
  "consumo-api": {
    caption: "Consumo de API: a resposta do parceiro é entrada externa — confira o contrato antes de usar.",
    body: () => (
      <Compare
        bad={[
          "Grava o que vier (hoje)",
          <>
            <span>O serviço grava o valor como veio, mesmo muito acima do teto.</span>
            <span>Um campo fora do contrato ({c("aprovacao_automatica")}) decide o status.</span>
          </>,
        ]}
        good={[
          "Confere o contrato",
          <>
            <span>Só aceita os campos combinados e o valor dentro da faixa; o resto vira {c("RespostaInvalida")}.</span>
            <span>O status é decisão do app: sempre {c("em análise")}.</span>
          </>,
        ]}
      />
    ),
  },
  "paginacao-teto": {
    caption: "Consumo de recursos: o servidor decide o tamanho máximo da página, não o cliente.",
    body: () => (
      <Compare
        bad={[
          "Limite do cliente (hoje)",
          <>
            <span>{c("?limite=100000")} faz o servidor ler e montar a base inteira numa resposta.</span>
            <span>{c("?limite=-1")} também abre tudo: no SQLite, {c("LIMIT -1")} é "sem limite".</span>
          </>,
        ]}
        good={[
          "Teto no servidor",
          <>
            <span>O serviço prende o limite: {c("max(1, min(limite, 100))")}.</span>
            <span>O app oficial, que pede 20, não percebe diferença.</span>
          </>,
        ]}
      />
    ),
  },
  "bfla": {
    caption: "Autorização de função (BFLA): autenticar não é autorizar — cada função sensível confere o papel.",
    body: () => (
      <Compare
        bad={[
          "Só exige login (hoje)",
          <>
            <span>A API de admin só checa {c("login_obrigatorio")}: qualquer logado passa.</span>
            <span>Um usuário comum chama {c("/api/admin/usuarios")} direto e recebe a lista toda.</span>
          </>,
        ]}
        good={[
          "Confere o papel na função",
          <>
            <span>Antes de executar, exige {c('papel == "admin"')}; o comum recebe 403.</span>
            <span>O papel vem da sessão (do banco), não de um campo do pedido.</span>
          </>,
        ]}
      />
    ),
  },
  "confianca-cliente": {
    caption: "Não confie em dado que o cliente controla e que o servidor pode determinar sozinho.",
    body: () => (
      <Compare
        bad={[
          "Confia no custo do formulário (hoje)",
          <>
            <span>O pedido manda {c("produto_id=1&custo=1")}; o servidor debita {c("custo")} = 1.</span>
            <span>Campo {c('type="hidden"')} é editável: leva um produto de 300 por 1 ponto.</span>
          </>,
        ]}
        good={[
          "Usa o custo do produto no banco",
          <>
            <span>O servidor ignora o {c("custo")} do formulário e lê {c("produto.custo")} do banco.</span>
            <span>O cliente só escolhe qual produto; o preço é consequência, decidida no servidor.</span>
          </>,
        ]}
      />
    ),
  },
  "path-traversal": {
    caption: "Path traversal: um nome com ../ (ou absoluto) sai da pasta permitida e lê outros arquivos.",
    body: () => (
      <Compare
        bad={[
          "Junta a pasta com o nome (o que tem hoje)",
          <>
            <span>{c('open(BASE + "/" + nome)')} abre o que vier: {c("../segredo_interno.txt")} sai da pasta.</span>
            <span>Um caminho absoluto como {c("/workspace/segredo_interno.txt")} ignora a pasta base inteira.</span>
          </>,
        ]}
        good={[
          "Confere que o caminho fica dentro da base",
          <>
            <span>Resolve o caminho final com {c("realpath")} e exige que ele comece dentro da pasta.</span>
            <span>Qualquer caminho que escape da pasta de documentos é recusado.</span>
          </>,
        ]}
      />
    ),
  },
  "cors-reflexo": {
    caption: "CORS: refletir a origem recebida libera qualquer site a ler a API — com o cookie da vítima.",
    body: () => (
      <Compare
        bad={[
          "Reflete qualquer origem (o que tem hoje)",
          <>
            <span>A API devolve {c("Access-Control-Allow-Origin: <a origem que chegou>")}, seja qual for.</span>
            <span>Com {c("Allow-Credentials: true")}, um site malicioso lê a API usando o cookie da vítima.</span>
          </>,
        ]}
        good={[
          "Lista de origens confiáveis",
          <>
            <span>Só origens de uma lista fixa recebem {c("Access-Control-Allow-Origin")}.</span>
            <span>Para qualquer outra origem, a API não devolve cabeçalho de CORS nenhum.</span>
          </>,
        ]}
      />
    ),
  },
  "forca-bruta": {
    caption: "Força bruta: sem limite de tentativas, o atacante testa senha após senha até acertar.",
    body: () => (
      <Compare
        bad={[
          "Sem limite (o que tem hoje)",
          <>
            <span>Cada senha errada responde só {c("inválido")}; ninguém conta as tentativas.</span>
            <span>O atacante manda {c("senha1, senha2, senha3…")} direto para {c("/login")}, sem parar.</span>
          </>,
        ]}
        good={[
          "Com limite por usuário no servidor",
          <>
            <span>O servidor conta as falhas por usuário e bloqueia depois de {c("5")}.</span>
            <span>A força bruta trava; um usuário diferente, que não errou, continua entrando.</span>
          </>,
        ]}
      />
    ),
  },
  "graphql-bola": {
    caption: "BOLA: a API confere o login, mas devolve o objeto pelo id sem checar o dono — troque o id e leia o de outro.",
    body: () => (
      <Compare
        bad={[
          "Resolve só pelo id (o que tem hoje)",
          <>
            <span>{c("pedido(id: 2)")} devolve o objeto mesmo que ele seja de outro usuário.</span>
            <span>Logado como o dono do {c("id 1")}, um laço de {c("id = 1, 2, 3…")} baixa os objetos de todos.</span>
          </>,
        ]}
        good={[
          "Confere o dono de cada objeto",
          <>
            <span>O resolver compara {c("pedido.dono_id")} com o usuário logado antes de devolver.</span>
            <span>Objeto de outro dono: {c("acesso negado")}. Estar logado não basta; cada objeto checa o dono.</span>
          </>,
        ]}
      />
    ),
  },
  "mob-chave-embutida": {
    caption: "Chave embutida: o pacote do app é público, então a chave que vem nele abre a API para qualquer um.",
    body: () => (
      <Compare
        bad={[
          "Libera pela chave do pacote (o que tem hoje)",
          <>
            <span>O app manda {c("X-Api-Key")} igual para todo mundo; ela está em {c("cliente/config.json")}.</span>
            <span>Quem abre o pacote chama {c("/api/itens?conta=2")} só com a chave e lê a conta de outro.</span>
          </>,
        ]}
        good={[
          "Exige o token do usuário",
          <>
            <span>O servidor identifica o usuário pelo {c("token")} emitido no login.</span>
            <span>Só devolve a lista se a conta pedida for a dona do token; a chave do pacote não vale nada sozinha.</span>
          </>,
        ]}
      />
    ),
  },
  "mob-dados-locais": {
    caption: "Armazenamento inseguro: o que o app grava no aparelho pode ser copiado e lido por quem pegar o celular.",
    body: () => (
      <Compare
        bad={[
          "Grava a senha no aparelho (o que tem hoje)",
          <>
            <span>Depois do login, {c("prefs")} recebe {c("senha = ...")} em texto puro.</span>
            <span>Perícia, backup ou malware copiam os arquivos do app e leem a senha.</span>
          </>,
        ]}
        good={[
          "Guarda só o token",
          <>
            <span>O app grava só {c("login")} e {c("token")}; a senha não sai da tela de login.</span>
            <span>O token é curto e o servidor pode revogá-lo; a senha nunca fica no aparelho.</span>
          </>,
        ]}
      />
    ),
  },
  "mob-biometria-cliente": {
    caption: "Biometria só no cliente: a tela pede a digital, mas a API executa sem conferir prova nenhuma.",
    body: () => (
      <Compare
        bad={[
          "Confia na tela do app (o que tem hoje)",
          <>
            <span>O app mostra {c("Confirme com a digital")} e depois chama {c("POST /api/acao")}.</span>
            <span>Quem chama a API direto, com o token, pula a digital e a operação é executada.</span>
          </>,
        ]}
        good={[
          "O servidor exige a prova",
          <>
            <span>A operação só roda com {c("X-Prova-Biometria")} válida, desta conta e com menos de 60 s.</span>
            <span>Sem prova, prova velha ou inventada: {c("401")}.</span>
          </>,
        ]}
      />
    ),
  },
  "mob-sessao-logout": {
    caption: "Sessão que não morre: o app esquece o token no logout, mas o servidor continua aceitando.",
    body: () => (
      <Compare
        bad={[
          "Só o app esquece (o que tem hoje)",
          <>
            <span>{c("POST /api/sair")} responde 204, mas o token segue ativo no banco.</span>
            <span>Quem copiou o token chama {c("/api/conta")} e entra na conta depois do logout.</span>
          </>,
        ]}
        good={[
          "O servidor revoga",
          <>
            <span>No logout, o servidor marca o token como revogado.</span>
            <span>Token antigo: {c("401")}. Sair encerra a sessão para todo mundo que tinha o token.</span>
          </>,
        ]}
      />
    ),
  },
  "mob-dados-demais": {
    caption: "Dados demais: a tela mostra só o nome, mas a API entrega o registro inteiro ao aparelho.",
    body: () => (
      <Compare
        bad={[
          "Devolve o registro inteiro (o que tem hoje)",
          <>
            <span>{c("GET /api/perfil")} traz {c("documento")} e {c("dado_pessoal")} junto com o nome.</span>
            <span>A tela esconde, mas um proxy ou um log mostra tudo.</span>
          </>,
        ]}
        good={[
          "Só o que a tela usa",
          <>
            <span>A API monta a resposta com {c("nome")} e {c("resumo")}, campo por campo.</span>
            <span>O que não sai do servidor não vaza pelo aparelho, pela rede nem por um log.</span>
          </>,
        ]}
      />
    ),
  },
  "mob-modo-teste": {
    caption: "Modo de teste esquecido: um cabeçalho do app de homologação ainda pula o login na produção.",
    body: () => (
      <Compare
        bad={[
          "Atalho de teste ativo (o que tem hoje)",
          <>
            <span>{c("X-Debug: 1")} faz a API tratar o pedido como da conta 1.</span>
            <span>Sem login nenhum, {c("/api/conta")} devolve os dados de outra pessoa.</span>
          </>,
        ]}
        good={[
          "Só o token identifica",
          <>
            <span>O atalho sai do build de produção.</span>
            <span>Sem token válido: {c("401")}, com ou sem {c("X-Debug")}.</span>
          </>,
        ]}
      />
    ),
  },
  "ldap-injection": {
    caption: "Injeção de LDAP: o nome entra cru no filtro, então um * vira curinga e lista o diretório inteiro.",
    body: () => (
      <Compare
        bad={[
          "Junta o nome cru no filtro (o que tem hoje)",
          <>
            <span>{c('filtro = f"(cn={nome})"')} usa o texto como está.</span>
            <span>Buscar por {c("*")} vira {c("(cn=*)")}: o curinga casa com todo mundo e vaza o diretório.</span>
          </>,
        ]}
        good={[
          "Escapa os caracteres especiais do filtro",
          <>
            <span>Antes de montar o filtro, troca {c("*")} por {c("\\2a")}, {c("(")} por {c("\\28")}, e assim por diante.</span>
            <span>Escapado, o {c("*")} vira texto: {c("(cn=\\2a)")} procura o caractere literal e não casa com ninguém.</span>
          </>,
        ]}
      />
    ),
  },
  "logica-validacao": {
    caption: "Falha de lógica: o código funciona, mas ninguém conferiu quando o valor pedido é válido.",
    body: () => (
      <Compare
        bad={[
          "Sem validação (o que tem hoje)",
          <>
            <span>O serviço debita {c("valor")} direto: aceita acima do saldo, zero ou negativo.</span>
            <span>Resgatar {c("999999")} de um saldo de {c("500")}, ou {c("-50")} (que credita o usuário), passa.</span>
          </>,
        ]}
        good={[
          "Com validação no servidor",
          <>
            <span>Antes de debitar: recusa se {c("valor <= 0")} e se {c("valor > conta.saldo")}.</span>
            <span>Só um valor positivo e dentro do saldo é debitado.</span>
          </>,
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
