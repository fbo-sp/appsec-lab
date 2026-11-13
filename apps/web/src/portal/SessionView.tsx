import { useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { api, type LabSession } from "./api";
import { StepPanel } from "./StepPanel";
import { Splitter, useStepsWidth } from "./Splitter";
import { ValidationLog } from "./ValidationLog";

type Tab = "app" | "code" | "terminal" | "log";
const TABS: { id: Tab; label: string }[] = [
  { id: "app", label: "Aplicação" },
  { id: "code", label: "Código" },
  { id: "terminal", label: "Terminal" },
  { id: "log", label: "Validação" },
];
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

function useNow() {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  return now;
}

function mmss(totalSeconds: number) {
  const left = Math.max(0, Math.floor(totalSeconds));
  return `${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}`;
}

const WARN_SECONDS = 5 * 60;

export function SessionView({ id }: { id: string }) {
  const [session, setSession] = useState<LabSession>();
  const [error, setError] = useState<string>();
  const [frames, setFrames] = useState<{
    workspace: string;
    workspaceOrigin: string;
    preview: string;
    previewOrigin: string;
  }>();
  const [tab, setTab] = useState<Tab>("app");
  const [split, setSplit] = useState(false);
  const [progressVersion, setProgressVersion] = useState(0);
  const workspaceFrame = useRef<HTMLIFrameElement>(null);
  const workbench = useRef<HTMLDivElement>(null);
  const steps = useStepsWidth(workbench);
  const [resizing, setResizing] = useState(false);
  const [previewKey, setPreviewKey] = useState(0);
  const [ending, setEnding] = useState(false);
  const fetchingTickets = useRef(false);
  const now = useNow();
  const secondsLeft = session ? (Date.parse(session.expiresAt) - now) / 1000 : 0;
  const left = mmss(secondsLeft);
  const [renewDismissedFor, setRenewDismissedFor] = useState<string>();
  const [renewing, setRenewing] = useState(false);
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
    // Ao voltar para a aba (ou acordar da suspensão), revalida já: o servidor é a fonte de verdade.
    const revalidate = () => {
      if (document.visibilityState !== "visible") return;
      clearTimeout(timer);
      tick();
    };
    document.addEventListener("visibilitychange", revalidate);
    window.addEventListener("focus", revalidate);
    return () => {
      stop = true;
      clearTimeout(timer);
      document.removeEventListener("visibilitychange", revalidate);
      window.removeEventListener("focus", revalidate);
    };
  }, [id]);

  // Ao ficar pronta: tickets de uso único para workspace e preview.
  useEffect(() => {
    if (!session || !LIVE.has(session.status) || frames || fetchingTickets.current) return;
    fetchingTickets.current = true;
    (async () => {
      try {
        const [ws, pv] = await Promise.all([api.ticket(id, "workspace"), api.ticket(id, "preview")]);
        setFrames({
          workspace: ws.url,
          workspaceOrigin: new URL(ws.url).origin,
          preview: pv.url,
          previewOrigin: new URL(pv.url).origin,
        });
        setSession(await api.session(id)); // READY -> ACTIVE na primeira conexão
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        fetchingTickets.current = false;
      }
    })();
  }, [session, frames, id]);

  const showApp = tab === "app" || (split && tab === "code");
  const showWorkspace = tab === "code" || tab === "terminal";
  const wsView = tab === "terminal" ? "terminal" : "code";

  // Diz ao workspace (outra origem) qual parte mostrar; o iframe nunca é recriado, então o terminal
  // e o arquivo aberto continuam vivos ao trocar de aba.
  // Só envia depois do onLoad: antes disso o iframe ainda está em about:blank (outra origem).
  const workspaceLoaded = useRef(false);
  const syncWorkspaceView = () => {
    if (!frames || !workspaceLoaded.current) return;
    workspaceFrame.current?.contentWindow?.postMessage({ type: "cecyber:view", view: wsView }, frames.workspaceOrigin);
  };
  useEffect(syncWorkspaceView, [wsView, frames]);

  function pickTab(t: Tab) {
    setTab(t);
    if (t !== "app" && t !== "code") setSplit(false);
  }

  function toggleSplit() {
    setSplit((v) => !v);
    setTab("code");
  }

  async function finishAndExit() {
    try {
      await api.terminate(id);
    } catch {
      /* a sessão expira sozinha; voltar ao painel não depende disso */
    }
    go("/");
  }

  async function renew() {
    setRenewing(true);
    try {
      setSession(await api.renew(id));
      setError(undefined);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRenewing(false);
    }
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
            <span
              className={`timer ${secondsLeft <= WARN_SECONDS ? "timer-warn" : ""}`}
              title={`Tempo restante da sessão. Renovações: ${session.renewals}/${session.maxRenewals}`}
            >
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
      {LIVE.has(status) && secondsLeft <= WARN_SECONDS && secondsLeft > 0 && (
        session.renewableAt && now >= Date.parse(session.renewableAt) ? (
          renewDismissedFor !== session.expiresAt && (
            <div className="overlay" role="alertdialog" aria-modal="true" aria-labelledby="renew-title">
              <div className="card renew">
                <div className="renew-clock" aria-hidden="true">⏳</div>
                <h2 id="renew-title">Sua sessão termina em {left}</h2>
                <p className="muted">
                  Quer continuar? Renovando, o prazo volta a {session.ttlMinutes} minutos. Restam{" "}
                  {session.maxRenewals - session.renewals} de {session.maxRenewals} renovações.
                </p>
                <p className="muted small">Se o prazo acabar, o ambiente é removido, mas seu progresso fica salvo.</p>
                <div className="summary-actions">
                  <button className="link" onClick={() => setRenewDismissedFor(session.expiresAt)}>
                    Agora não
                  </button>
                  <button className="primary" onClick={renew} disabled={renewing} autoFocus>
                    {renewing ? "Renovando…" : `Renovar por ${session.ttlMinutes} min`}
                  </button>
                </div>
              </div>
            </div>
          )
        ) : (
          !session.renewableAt && (
            <div className="banner-warn" role="status">
              ⏳ Sua sessão termina em {left} e não há mais renovações. Seu progresso fica salvo; para continuar
              depois, inicie uma nova sessão.
            </div>
          )
        )
      )}

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
        <div
          ref={workbench}
          className={`workbench ${resizing ? "resizing" : ""}`}
          style={{ "--steps-w": `${steps.width}px` } as CSSProperties}
        >
          <aside className="steps">
            <StepPanel
              sessionId={id}
              onExit={finishAndExit}
              onProgress={() => setProgressVersion((v) => v + 1)}
              onShowLog={() => pickTab("log")}
            />
          </aside>
          <Splitter
            width={steps.width}
            min={steps.min}
            max={steps.max}
            onChange={steps.setWidth}
            onDragging={setResizing}
          />
          <section className="panes">
            <div className="tabbar">
              <div className="tabs" role="tablist" aria-label="Áreas do laboratório">
                {TABS.map((t) => {
                  const selected = tab === t.id || (split && t.id === "app" && tab === "code");
                  return (
                    <button
                      key={t.id}
                      role="tab"
                      aria-selected={selected}
                      className={`tab ${selected ? "tab-on" : ""}`}
                      onClick={() => pickTab(t.id)}
                    >
                      {t.label}
                    </button>
                  );
                })}
              </div>
              <div className="tab-tools">
                {showApp && frames && (
                  <>
                    <button className="link" onClick={() => setPreviewKey((k) => k + 1)}>
                      recarregar
                    </button>
                    <a className="link" href={`${frames.previewOrigin}/`} target="_blank" rel="noreferrer">
                      abrir em nova aba
                    </a>
                  </>
                )}
                <button
                  className={`split-toggle ${split ? "on" : ""}`}
                  aria-pressed={split}
                  onClick={toggleSplit}
                  title="Ver código e aplicação lado a lado"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <rect x="3" y="4" width="18" height="16" rx="2" />
                    <path d="M12 4v16" />
                  </svg>
                  Código + Aplicação
                </button>
              </div>
            </div>
            {frames ? (
              <div className={`tab-body ${split && tab === "code" ? "split" : ""}`}>
                <iframe
                  ref={workspaceFrame}
                  className="pane-workspace"
                  title="Editor e terminal"
                  src={frames.workspace}
                  hidden={!showWorkspace}
                  onLoad={() => {
                    workspaceLoaded.current = true;
                    syncWorkspaceView();
                  }}
                />
                <iframe
                  key={previewKey}
                  className="pane-preview"
                  title="Aplicação do laboratório"
                  src={previewKey === 0 ? frames.preview : `${frames.previewOrigin}/`}
                  sandbox="allow-scripts allow-forms allow-same-origin allow-popups"
                  hidden={!showApp}
                />
                {tab === "log" && <ValidationLog sessionId={id} version={progressVersion} />}
              </div>
            ) : (
              <div className="muted pad">Conectando ao ambiente…</div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
