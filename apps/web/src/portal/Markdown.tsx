import { useState } from "react";
import type { ReactNode } from "react";
import { parseMarkdown, type Inline } from "./markdown";

/** Renderiza o Markdown restrito do conteúdo das etapas (ADR-012) somente com elementos React. */
/** Ajudas contextuais: um termo em **negrito** cujo texto (sem diferenciar maiúsculas) é uma chave do mapa
 * ganha, logo depois dele, o elemento devolvido (por exemplo, o ícone "i" da barra de endereço). */
export type TermHelp = Record<string, () => ReactNode>;

export function Markdown({ text, className, terms }: { text: string; className?: string; terms?: TermHelp }) {
  const blocks = parseMarkdown(text);
  const inline = (nodes: Inline[]) => renderInline(nodes, terms);
  return (
    <div className={`md ${className ?? ""}`}>
      {blocks.map((b, i) => {
        switch (b.t) {
          case "p":
            return <p key={i}>{inline(b.c)}</p>;
          case "ul":
            return (
              <ul key={i}>
                {b.items.map((it, j) => (
                  <li key={j}>{inline(it)}</li>
                ))}
              </ul>
            );
          case "ol":
            return (
              <ol key={i} start={b.start}>
                {b.items.map((it, j) => (
                  <li key={j}>{inline(it)}</li>
                ))}
              </ol>
            );
          case "pre":
            return <CodeBlock key={i} lang={b.lang} code={b.v} />;
        }
      })}
    </div>
  );
}

function plain(nodes: Inline[]): string {
  return nodes.map((n) => (n.t === "text" || n.t === "code" ? n.v : plain(n.c))).join("");
}

function renderInline(nodes: Inline[], terms?: TermHelp): ReactNode[] {
  const inline = (c: Inline[]) => renderInline(c, terms);
  return nodes.map((n, i) => {
    switch (n.t) {
      case "text":
        return n.v;
      case "code":
        return <code key={i}>{n.v}</code>;
      case "strong": {
        const help = terms?.[plain(n.c).trim().toLowerCase()];
        return help ? (
          <span key={i} className="md-term">
            <strong>{inline(n.c)}</strong>
            {help()}
          </span>
        ) : (
          <strong key={i}>{inline(n.c)}</strong>
        );
      }
      case "em":
        return <em key={i}>{inline(n.c)}</em>;
      case "link":
        return (
          <a key={i} href={n.href} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">
            {inline(n.c)}
          </a>
        );
    }
  });
}

function CodeBlock({ lang, code }: { lang: string; code: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* área de transferência indisponível: o aluno pode selecionar o texto */
    }
  }
  return (
    <div className="md-code">
      <div className="md-code-bar">
        <span>{lang || "código"}</span>
        <button type="button" className="link" onClick={copy}>
          {copied ? "copiado" : "copiar"}
        </button>
      </div>
      <pre>
        <code>{code}</code>
      </pre>
    </div>
  );
}

export function References({ items }: { items?: { title: string; url: string }[] | null }) {
  if (!items?.length) return null;
  return (
    <ul className="md-refs">
      {items.map((r) => (
        <li key={r.url}>
          <a href={r.url} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">
            {r.title}
          </a>
        </li>
      ))}
    </ul>
  );
}
