import { useEffect, useRef, useState } from "react";
import { api, type LabSession } from "./api";
import { StepPanel } from "./StepPanel";
import { ErrorBox, StatusChip, go } from "./App";

const LIVE = new Set(["READY", "ACTIVE"]);
const ENDED = new Set(["TERMINATED", "EXPIRED", "FAILED", "COMPLETED"]);
const PREPARING = ["REQUESTED", "PROVISIONING", "READY"];
const STAGE: Record<string, { title: string; detail: string }> = {
  REQUESTED: { title: "Solicitação registrada", detail: "Sua sessão entrou na fila de preparação." },
  PROVISIONING: {
    title: "Criando ambiente isolado",
    detail: "Montando um contêiner exclusivo, com rede própria e seus arquivos de trabalho. Aguarde…",
  },
  READY: { title: "Pronto", detail: "" },
};
const TIPS = [
  "Seu ambiente é exclusivo e temporário: nada do que você fizer afeta outros alunos.",
  "As dicas não descontam pontos. Use quando travar.",
  "Você pode validar cada etapa quantas vezes precisar.",
  "A validação testa uma cópia da sua aplicação, fora do seu editor.",
];

function useElapsed(active: boolean) {
  const [start] = useState(Date.now());
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!active) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [active]);
  return Math.max(0, Math.floor((now - start) / 1000));
}

function useCountdown(expiresAt?: string) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  if (!expiresAt) return "";
  const left = Math.max(0, Math.floor((Date.parse(expiresAt) - now) / 1000));
  return `${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}`;
}

export function SessionView({ id }: { id: string }) {
  const [session, setSession] = useState<LabSession>();
  const [error, setError] = useState<string>();
  const [frames, setFrames] = useState<{ workspace: string; preview: string; previewOrigin: string }>();
  const [previewKey, setPreviewKey] = useState(0);
  const [ending, setEnding] = useState(false);
  const fetchingTickets = useRef(false);
  const left = useCountdown(session?.expiresAt);
  const waited = useElapsed(!session || !LIVE.has(session.status));

  // Acompanha o estado da sessão (o backend é a fonte de verdade).
  useEffect(() => {
    let stop = false;
    let timer: ReturnType<typeof setTimeout>;
    const tick = async () => {
      try {
        const s = await api.session(id);
        if (stop) return;
        setSession(s);
        setError(undefined);
        if (!ENDED.has(s.status)) timer = setTimeout(tick, LIVE.has(s.status) ? 5000 : 1000);
      } catch (e) {
        if (!stop) setError(e instanceof Error ? e.message : String(e));
        if (!stop) timer = setTimeout(tick, 3000);
      }
    };
    tick();
    return () => {
      stop = true;
      clearTimeout(timer);
    };
  }, [id]);

  // Ao ficar pronta: tickets de uso único para workspace e preview.
  useEffect(() => {
    if (!session || !LIVE.has(session.status) || frames || fetchingTickets.current) return;
    fetchingTickets.current = true;
    (async () => {
      try {
        const [ws, pv] = await Promise.all([api.ticket(id, "workspace"), api.ticket(id, "preview")]);
        setFrames({ workspace: ws.url, preview: pv.url, previewOrigin: new URL(pv.url).origin });
        setSession(await api.session(id)); // READY -> ACTIVE na primeira conexão
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        fetchingTickets.current = false;
      }
    })();
  }, [session, frames, id]);

  async function finishAndExit() {
    try {
      await api.terminate(id);
    } catch {
      /* a sessão expira sozinha; voltar ao painel não depende disso */
    }
    go("/");
  }

  async function terminate() {
    if (!confirm("Encerrar a sessão? O ambiente e os arquivos editados serão descartados.")) return;
    setEnding(true);
    try {
      setSession(await api.terminate(id));
      setFrames(undefined);
      const poll = async () => {
        const s = await api.session(id);
        setSession(s);
        if (!ENDED.has(s.status)) setTimeout(poll, 1000);
      };
      poll();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setEnding(false);
    }
  }

  if (!session) return <main className="page muted">{error ? <ErrorBox message={error} /> : "Carregando sessão…"}</main>;

  const status = session.status;

  return (
    <div className="session">
      <div className="session-bar">
        <div>
          <a className="back" href="#/">← Laboratórios</a>
          <strong className="session-title">
            {session.labId} · {session.variantId}
          </strong>
          <StatusChip status={status} />
        </div>
        <div className="session-actions">
          {LIVE.has(status) && (
            <span className="timer" title="Tempo restante da sessão">
              ⏱ {left}
            </span>
          )}
          {!ENDED.has(status) && status !== "TERMINATING" && (
            <button className="danger" onClick={terminate} disabled={ending}>
              Encerrar sessão
            </button>
          )}
        </div>
      </div>
      {error && <ErrorBox message={error} />}

      {!LIVE.has(status) && !ENDED.has(status) && status !== "TERMINATING" && (
        <main className="page narrow">
          <div className="card preparing">
            <h2>Preparando seu ambiente</h2>
            <ol className="progress">
              {PREPARING.map((p, i) => {
                // A solicitação já está registrada quando esta tela aparece; o tempo é gasto na criação.
                const at = status === "READY" ? 3 : 1;
                const state = i < at ? "done" : i === at ? "active" : "";
                return (
                  <li key={p} className={state}>
                    <span className="progress-icon" aria-hidden="true">
                      {state === "done" ? "✓" : state === "active" ? <span className="spinner" /> : "○"}
                    </span>
                    <span>
                      {STAGE[p].title}
                      {state === "active" && <span className="stage-detail">{STAGE[p].detail}</span>}
                    </span>
                  </li>
                );
              })}
            </ol>
            <div className="indeterminate" aria-hidden="true">
              <span />
            </div>
            <p className="muted small" aria-live="polite">
              Tempo decorrido: {waited}s. Na primeira sessão pode levar até um minuto; não feche esta página.
            </p>
            <p className="tip small">💡 {TIPS[Math.floor(waited / 6) % TIPS.length]}</p>
          </div>
        </main>
      )}

      {(ENDED.has(status) || status === "TERMINATING") && (
        <main className="page narrow">
          <div className="card">
            <h2>{status === "TERMINATING" ? "Encerrando a sessão…" : "Sessão finalizada"}</h2>
            <p className="muted">
              {status === "FAILED"
                ? `Não foi possível preparar o ambiente (${session.lastErrorCode ?? "erro"}). Tente iniciar novamente.`
                : status === "EXPIRED"
                  ? "O prazo da sessão terminou e o ambiente foi removido."
                  : "O ambiente e os arquivos temporários foram removidos."}
            </p>
            <button className="primary" onClick={() => go(`/labs/${session.labId}/${session.version}`)}>
              Voltar ao laboratório
            </button>
          </div>
        </main>
      )}

      {LIVE.has(status) && (
        <div className="workbench">
          <aside className="steps">
            <StepPanel sessionId={id} onExit={finishAndExit} />
          </aside>
          <section className="panes">
            {frames ? (
              <>
                <div className="pane-preview">
                  <div className="preview-bar">
                    <span>Aplicação do laboratório</span>
                    <span>
                      <button className="link" onClick={() => setPreviewKey((k) => k + 1)}>
                        recarregar
                      </button>
                      <a className="link" href={`${frames.previewOrigin}/`} target="_blank" rel="noreferrer">
                        abrir em nova aba
                      </a>
                    </span>
                  </div>
                  <iframe
                    key={previewKey}
                    title="Aplicação do laboratório"
                    src={previewKey === 0 ? frames.preview : `${frames.previewOrigin}/`}
                    sandbox="allow-scripts allow-forms allow-same-origin allow-popups"
                  />
                </div>
                <iframe className="pane-workspace" title="Editor e terminal" src={frames.workspace} />
              </>
            ) : (
              <div className="muted pad">Conectando ao ambiente…</div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
