import type { ReactNode } from "react";

/**
 * Ilustrações fixas da interface para o texto das etapas (ADR-018, extensão do ADR-012).
 *
 * No Markdown restrito, um bloco cercado com a linguagem `ilustracao` e um nome conhecido vira um
 * desenho da própria tela, feito só com elementos React e CSS: nada vem de fora nem do manifesto além
 * do nome. Nome desconhecido continua aparecendo como bloco de código.
 */
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
