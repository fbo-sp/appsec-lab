import { describe, expect, it } from "vitest";
import { isSafeHref, parseInline, parseMarkdown } from "./markdown";

describe("parseMarkdown", () => {
  it("joins paragraph lines and splits on blank lines", () => {
    expect(parseMarkdown("um\ndois\n\ntrês")).toEqual([
      { t: "p", c: [{ t: "text", v: "um dois" }] },
      { t: "p", c: [{ t: "text", v: "três" }] },
    ]);
  });

  it("keeps fenced code verbatim, including markup-looking text", () => {
    const src = "```python\nsql = f\"... '{termo}' **x**\"\n<script>alert(1)</script>\n```";
    expect(parseMarkdown(src)).toEqual([
      { t: "pre", lang: "python", v: "sql = f\"... '{termo}' **x**\"\n<script>alert(1)</script>" },
    ]);
  });

  it("treats an unterminated fence as code until the end", () => {
    expect(parseMarkdown("```\nabc")).toEqual([{ t: "pre", lang: "", v: "abc" }]);
  });

  it("parses bullet and ordered lists", () => {
    expect(parseMarkdown("- a\n- `b`\n\n3. c\n4. d")).toEqual([
      { t: "ul", items: [[{ t: "text", v: "a" }], [{ t: "code", v: "b" }]] },
      { t: "ol", start: 3, items: [[{ t: "text", v: "c" }], [{ t: "text", v: "d" }]] },
    ]);
  });

  it("never produces HTML nodes: tags stay text", () => {
    const blocks = parseMarkdown('<img src=x onerror="alert(1)"> <b>oi</b>');
    expect(blocks).toEqual([{ t: "p", c: [{ t: "text", v: '<img src=x onerror="alert(1)"> <b>oi</b>' }] }]);
  });
});

describe("parseInline", () => {
  it("parses code, strong, em and https links", () => {
    expect(parseInline("use `?` e **não** *concatene* [OWASP](https://owasp.org/x)")).toEqual([
      { t: "text", v: "use " },
      { t: "code", v: "?" },
      { t: "text", v: " e " },
      { t: "strong", c: [{ t: "text", v: "não" }] },
      { t: "text", v: " " },
      { t: "em", c: [{ t: "text", v: "concatene" }] },
      { t: "text", v: " " },
      { t: "link", href: "https://owasp.org/x", c: [{ t: "text", v: "OWASP" }] },
    ]);
  });

  it.each(["javascript:alert(1)", "http://owasp.org", "data:text/html,x", "//owasp.org", "https://a.b/\"x"])(
    "renders a link with unsafe href %s as plain text",
    (href) => {
      const nodes = parseInline(`[clique](${href})`);
      expect(nodes.every((n) => n.t === "text")).toBe(true);
    },
  );

  it("does not treat SQL comments or lone asterisks as emphasis", () => {
    expect(parseInline("SELECT * FROM medicos --")).toEqual([{ t: "text", v: "SELECT * FROM medicos --" }]);
  });

  it("supports escapes", () => {
    expect(parseInline("\\*literal\\*")).toEqual([{ t: "text", v: "*literal*" }]);
  });
});

describe("isSafeHref", () => {
  it("matches the contract rule", () => {
    expect(isSafeHref("https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html")).toBe(
      true,
    );
    expect(isSafeHref("https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders")).toBe(true);
    expect(isSafeHref("javascript:alert(1)")).toBe(false);
  });
});
