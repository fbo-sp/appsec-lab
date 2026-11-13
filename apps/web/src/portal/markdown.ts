/**
 * Markdown RESTRITO para o conteúdo das etapas (ADR-012).
 *
 * Gera uma árvore de dados que o componente <Markdown> transforma em elementos React; nunca há HTML
 * cru nem `dangerouslySetInnerHTML`, então `<script>` e atributos injetados aparecem como texto.
 *
 * Suportado:
 * - blocos: parágrafos (linhas consecutivas), listas `- `/`* ` e `1. `, blocos de código cercados por ```
 * - inline: `código`, **negrito**, *itálico*, [texto](https://…) — links só com https
 */

export type Inline =
  | { t: "text"; v: string }
  | { t: "code"; v: string }
  | { t: "strong"; c: Inline[] }
  | { t: "em"; c: Inline[] }
  | { t: "link"; href: string; c: Inline[] };

export type Block =
  | { t: "p"; c: Inline[] }
  | { t: "ul"; items: Inline[][] }
  | { t: "ol"; start: number; items: Inline[][] }
  | { t: "pre"; lang: string; v: string };

const FENCE = /^```\s*([A-Za-z0-9_+-]*)\s*$/;
const BULLET = /^\s*[-*]\s+(.*)$/;
const ORDERED = /^\s*(\d{1,3})[.)]\s+(.*)$/;
// Mesma regra do contrato (packages/contracts): https, host simples, sem espaço, aspas ou < >.
const HTTPS = /^https:\/\/[A-Za-z0-9.-]+(:[0-9]{1,5})?(\/[^\s<>"'`]*)?$/;

export function isSafeHref(href: string): boolean {
  return href.length <= 500 && HTTPS.test(href);
}

export function parseMarkdown(source: string): Block[] {
  const lines = source.replace(/\r\n?/g, "\n").split("\n");
  const blocks: Block[] = [];
  let para: string[] = [];

  const flush = () => {
    if (para.length) blocks.push({ t: "p", c: parseInline(para.join(" ")) });
    para = [];
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const fence = FENCE.exec(line.trim());
    if (fence) {
      flush();
      const body: string[] = [];
      i++;
      while (i < lines.length && lines[i].trim() !== "```") body.push(lines[i++]);
      // Bloco sem fechamento: tudo até o fim vira código (nunca é interpretado).
      blocks.push({ t: "pre", lang: fence[1] ?? "", v: body.join("\n") });
      continue;
    }
    if (!line.trim()) {
      flush();
      continue;
    }
    const bullet = BULLET.exec(line);
    const ordered = bullet ? null : ORDERED.exec(line);
    if (bullet || ordered) {
      flush();
      const kind = bullet ? "ul" : "ol";
      const items: Inline[][] = [];
      const start = ordered ? Number(ordered[1]) : 1;
      while (i < lines.length) {
        const b = BULLET.exec(lines[i]);
        const o = b ? null : ORDERED.exec(lines[i]);
        const m = kind === "ul" ? b : o;
        if (m) {
          items.push(parseInline(kind === "ul" ? m[1] : m[2]));
          i++;
        } else if (lines[i].trim() && /^\s{2,}/.test(lines[i]) && items.length) {
          // Continuação indentada do item anterior.
          items[items.length - 1] = parseInline(joinText(items[items.length - 1]) + " " + lines[i].trim());
          i++;
        } else break;
      }
      i--;
      blocks.push(kind === "ul" ? { t: "ul", items } : { t: "ol", start, items });
      continue;
    }
    para.push(line.trim());
  }
  flush();
  return blocks;
}

// Reconstrói o texto-fonte aproximado de um item (só para juntar linhas de continuação).
function joinText(nodes: Inline[]): string {
  return nodes
    .map((n) => {
      switch (n.t) {
        case "text":
          return n.v;
        case "code":
          return "`" + n.v + "`";
        case "strong":
          return "**" + joinText(n.c) + "**";
        case "em":
          return "*" + joinText(n.c) + "*";
        case "link":
          return "[" + joinText(n.c) + "](" + n.href + ")";
      }
    })
    .join("");
}

export function parseInline(src: string, depth = 0): Inline[] {
  const out: Inline[] = [];
  let text = "";
  const pushText = () => {
    if (text) out.push({ t: "text", v: text });
    text = "";
  };
  let i = 0;
  while (i < src.length) {
    const ch = src[i];
    if (ch === "\\" && i + 1 < src.length && "\\`*_[]()".includes(src[i + 1])) {
      text += src[i + 1];
      i += 2;
      continue;
    }
    if (ch === "`") {
      const end = src.indexOf("`", i + 1);
      if (end > i) {
        pushText();
        out.push({ t: "code", v: src.slice(i + 1, end) });
        i = end + 1;
        continue;
      }
    }
    if (depth < 4 && src.startsWith("**", i)) {
      const end = src.indexOf("**", i + 2);
      if (end > i + 2) {
        pushText();
        out.push({ t: "strong", c: parseInline(src.slice(i + 2, end), depth + 1) });
        i = end + 2;
        continue;
      }
    }
    if (depth < 4 && ch === "*" && src[i + 1] !== " " && src[i + 1] !== "*") {
      const end = src.indexOf("*", i + 1);
      if (end > i + 1 && src[end - 1] !== " ") {
        pushText();
        out.push({ t: "em", c: parseInline(src.slice(i + 1, end), depth + 1) });
        i = end + 1;
        continue;
      }
    }
    if (depth < 4 && ch === "[") {
      const m = /^\[([^\]\n]{1,200})\]\(([^)\s]{1,500})\)/.exec(src.slice(i));
      if (m && isSafeHref(m[2])) {
        pushText();
        out.push({ t: "link", href: m[2], c: parseInline(m[1], depth + 1) });
        i += m[0].length;
        continue;
      }
    }
    text += ch;
    i++;
  }
  pushText();
  return out;
}
