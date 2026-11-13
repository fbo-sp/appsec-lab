import { useCallback, useEffect, useRef, useState, type JSX } from "react";
import { EditorView, basicSetup } from "codemirror";
import { EditorState, type Extension } from "@codemirror/state";
import { keymap } from "@codemirror/view";
import { python } from "@codemirror/lang-python";
import { html } from "@codemirror/lang-html";
import { javascript } from "@codemirror/lang-javascript";
import { sql } from "@codemirror/lang-sql";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { listDir, readFile, terminalUrl, writeFile, type Entry } from "./agent";

function language(path: string): Extension[] {
  if (path.endsWith(".py")) return [python()];
  if (/\.html?$/.test(path)) return [html()];
  if (/\.(m?js|ts|tsx|jsx|json)$/.test(path)) return [javascript({ typescript: /\.tsx?$/.test(path) })];
  if (path.endsWith(".sql")) return [sql()];
  return [];
}

type View = "both" | "code" | "terminal";

// O portal (única origem autorizada a embutir esta página: frame-ancestors) escolhe a visão pela aba
// ativa. Só aceitamos a mensagem do próprio pai e com formato exato; trocar a visão não dá acesso a nada.
function useViewFromParent(): View {
  const [view, setView] = useState<View>("both");
  useEffect(() => {
    const onMessage = (e: MessageEvent) => {
      if (e.source !== window.parent || window.parent === window) return;
      const d = e.data as { type?: unknown; view?: unknown } | null;
      if (d && d.type === "cecyber:view" && (d.view === "both" || d.view === "code" || d.view === "terminal")) {
        setView(d.view);
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);
  return view;
}

export function Workspace() {
  const paneView = useViewFromParent();
  const [tree, setTree] = useState<Record<string, Entry[]>>({});
  const [open, setOpen] = useState<Set<string>>(new Set([""]));
  const [file, setFile] = useState<string>();
  const [dirty, setDirty] = useState(false);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>();
  const editorEl = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | undefined>(undefined);
  const fileRef = useRef<string | undefined>(undefined);

  const loadDir = useCallback(async (path: string) => {
    try {
      const entries = await listDir(path);
      setTree((t) => ({ ...t, [path]: entries }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    loadDir("");
  }, [loadDir]);

  const save = useCallback(async () => {
    const path = fileRef.current;
    if (!path || !view.current) return;
    setStatus("Salvando…");
    try {
      await writeFile(path, view.current.state.doc.toString());
      setDirty(false);
      setStatus(`Salvo às ${new Date().toLocaleTimeString("pt-BR")}`);
    } catch (e) {
      setStatus("");
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  async function openFile(path: string) {
    if (dirty && !confirm("Há alterações não salvas. Descartar?")) return;
    setError(undefined);
    try {
      const content = await readFile(path);
      fileRef.current = path;
      setFile(path);
      setDirty(false);
      setStatus("");
      view.current?.destroy();
      view.current = new EditorView({
        parent: editorEl.current!,
        state: EditorState.create({
          doc: content,
          extensions: [
            basicSetup,
            ...language(path),
            keymap.of([{ key: "Mod-s", preventDefault: true, run: () => (save(), true) }]),
            EditorView.updateListener.of((u) => u.docChanged && setDirty(true)),
            EditorView.theme({ "&": { height: "100%" }, ".cm-scroller": { fontFamily: "ui-monospace, Consolas, monospace" } }),
          ],
        }),
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  function toggle(path: string) {
    setOpen((o) => {
      const n = new Set(o);
      if (n.has(path)) n.delete(path);
      else {
        n.add(path);
        loadDir(path);
      }
      return n;
    });
  }

  function renderDir(path: string, depth: number): JSX.Element[] {
    return (tree[path] ?? []).flatMap((e) => {
      const row = (
        <li key={e.path}>
          <button
            className={`entry ${e.path === file ? "active" : ""}`}
            style={{ paddingLeft: `${0.6 + depth * 0.9}rem` }}
            onClick={() => (e.type === "dir" ? toggle(e.path) : openFile(e.path))}
            title={e.path}
          >
            <span className="icon">{e.type === "dir" ? (open.has(e.path) ? "▾" : "▸") : "·"}</span>
            {e.name}
          </button>
        </li>
      );
      return e.type === "dir" && open.has(e.path) ? [row, ...renderDir(e.path, depth + 1)] : [row];
    });
  }

  return (
    <div className={`ws view-${paneView}`}>
      <aside className="files">
        <div className="files-head">
          <span>Arquivos</span>
          <button className="mini" title="Atualizar" onClick={() => Object.keys(tree).forEach(loadDir)}>
            ↻
          </button>
        </div>
        <ul>{renderDir("", 0)}</ul>
      </aside>
      <section className="editor-col">
        <div className="editor-head">
          <span className="file-name">{file ? `${file}${dirty ? " •" : ""}` : "Selecione um arquivo"}</span>
          <span className="editor-status">{status}</span>
          <button className="mini primary" onClick={save} disabled={!file || !dirty}>
            Salvar <kbd>Ctrl+S</kbd>
          </button>
        </div>
        {error && (
          <div className="ws-error" role="alert">
            {error} <button className="mini" onClick={() => setError(undefined)}>×</button>
          </div>
        )}
        <div className="editor" ref={editorEl}>
          {!file && <div className="placeholder">Escolha um arquivo à esquerda para editar.</div>}
        </div>
        <TerminalPane />
      </section>
    </div>
  );
}

function TerminalPane() {
  const el = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<"connecting" | "open" | "closed">("connecting");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const term = new Terminal({
      fontFamily: "ui-monospace, Consolas, monospace",
      fontSize: 13,
      cursorBlink: true,
      theme: { background: "#0f131a" },
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(el.current!);
    fit.fit();
    setState("connecting");
    const ws = new WebSocket(terminalUrl());
    const sendSize = () => ws.readyState === 1 && ws.send(JSON.stringify({ t: "r", c: term.cols, r: term.rows }));
    ws.onopen = () => {
      setState("open");
      sendSize();
    };
    ws.onmessage = (m) => term.write(typeof m.data === "string" ? m.data : "");
    ws.onclose = () => {
      setState("closed");
      term.write("\r\n\x1b[33m[terminal desconectado]\x1b[0m\r\n");
    };
    const sub = term.onData((d) => ws.readyState === 1 && ws.send(JSON.stringify({ t: "i", d })));
    const ro = new ResizeObserver(() => {
      fit.fit();
      sendSize();
    });
    ro.observe(el.current!);
    return () => {
      ro.disconnect();
      sub.dispose();
      ws.close();
      term.dispose();
    };
  }, [attempt]);

  return (
    <div className="terminal-wrap">
      <div className="terminal-head">
        <span>Terminal</span>
        {state === "closed" && (
          <button className="mini" onClick={() => setAttempt((a) => a + 1)}>
            reconectar
          </button>
        )}
        {state === "connecting" && <span className="dim">conectando…</span>}
      </div>
      <div className="terminal" ref={el} />
    </div>
  );
}
