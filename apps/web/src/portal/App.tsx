import { useCallback, useEffect, useState } from "react";
import { api, ApiError, currentUser, setUser, type Lab, type LabSession } from "./api";
import { SessionView } from "./SessionView";

type Route = { name: "catalog" } | { name: "lab"; labId: string; version: string } | { name: "session"; id: string };

function parse(hash: string): Route {
  const parts = hash.replace(/^#\/?/, "").split("/");
  if (parts[0] === "labs" && parts[1] && parts[2]) return { name: "lab", labId: parts[1], version: parts[2] };
  if (parts[0] === "sessions" && parts[1]) return { name: "session", id: parts[1] };
  return { name: "catalog" };
}

export function go(path: string): void {
  location.hash = path;
}

export function App() {
  const [user, setUserState] = useState(currentUser());
  const [route, setRoute] = useState<Route>(parse(location.hash));
  useEffect(() => {
    const on = () => setRoute(parse(location.hash));
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);

  if (!user) return <Login onLogin={(u) => (setUser(u), setUserState(u))} />;
  return (
    <div className="shell">
      <header className="topbar">
        <a className="brand" href="#/">
          <span className="brand-mark" aria-hidden>◆</span> CECyber AppSec Labs
        </a>
        <div className="topbar-right">
          <span className="dev-badge" title="Autenticação de desenvolvimento local; não use em produção">
            modo local
          </span>
          <span className="user">{user}</span>
          <button className="link" onClick={() => (setUser(null), setUserState(null))}>
            trocar usuário
          </button>
        </div>
      </header>
      {route.name === "catalog" && <Catalog />}
      {route.name === "lab" && <LabIntro labId={route.labId} version={route.version} />}
      {route.name === "session" && <SessionView id={route.id} />}
    </div>
  );
}

function Login({ onLogin }: { onLogin: (u: string) => void }) {
  const [name, setName] = useState("aluno1");
  const valid = /^[A-Za-z0-9._@-]{1,64}$/.test(name);
  return (
    <main className="login">
      <div className="card login-card">
        <h1>CECyber AppSec Labs</h1>
        <p className="muted">
          Ambiente de desenvolvimento local. O login real (OIDC) ainda não está disponível; escolha um nome de
          usuário de teste.
        </p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (valid) onLogin(name);
          }}
        >
          <label htmlFor="user">Usuário de teste</label>
          <input id="user" value={name} onChange={(e) => setName(e.target.value)} autoFocus />
          <button className="primary" disabled={!valid}>
            Entrar
          </button>
        </form>
      </div>
    </main>
  );
}

function useAsync<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [state, setState] = useState<{ data?: T; error?: string; loading: boolean }>({ loading: true });
  const run = useCallback(() => {
    setState((s) => ({ ...s, loading: true }));
    fn().then(
      (data) => setState({ data, loading: false }),
      (e: unknown) => setState({ error: e instanceof Error ? e.message : String(e), loading: false }),
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(run, [run]);
  return { ...state, reload: run };
}

const DIFFICULTY: Record<string, string> = {
  beginner: "Iniciante",
  intermediate: "Intermediário",
  advanced: "Avançado",
};

function Catalog() {
  const labs = useAsync(() => api.labs(), []);
  const sessions = useAsync(() => api.sessions(), []);
  return (
    <main className="page">
      <h1>Laboratórios</h1>
      <p className="muted">Ambientes efêmeros e isolados para praticar segurança de aplicações.</p>
      {sessions.data && sessions.data.items.length > 0 && (
        <section className="resume">
          <h2>Sessões em andamento</h2>
          {sessions.data.items.map((s) => (
            <div className="resume-row" key={s.sessionId}>
              <span>
                <strong>{s.labId}</strong> · {s.variantId} · <StatusChip status={s.status} />
              </span>
              <button onClick={() => go(`/sessions/${s.sessionId}`)}>Continuar</button>
            </div>
          ))}
        </section>
      )}
      {labs.loading && <p className="muted">Carregando…</p>}
      {labs.error && <ErrorBox message={labs.error} />}
      {labs.data && labs.data.items.length === 0 && (
        <div className="card empty">
          Nenhum laboratório publicado. Registre o LAB-000 com <code>scripts/lab-local.ps1</code>.
        </div>
      )}
      <div className="grid">
        {labs.data?.items.map((lab) => (
          <article className="card lab-card" key={`${lab.labId}@${lab.version}`}>
            <div className="lab-card-head">
              <span className="lab-id">{lab.labId}</span>
              <span className="tag">{lab.primaryCwe}</span>
            </div>
            <h3>{lab.title}</h3>
            <p className="muted small">
              {DIFFICULTY[lab.learning.difficulty] ?? lab.learning.difficulty} · ~{lab.learning.estimatedMinutes} min ·{" "}
              {lab.steps.length} {lab.steps.length === 1 ? "etapa" : "etapas"}
            </p>
            <button className="primary" onClick={() => go(`/labs/${lab.labId}/${lab.version}`)}>
              Abrir
            </button>
          </article>
        ))}
      </div>
    </main>
  );
}

function LabIntro({ labId, version }: { labId: string; version: string }) {
  const lab = useAsync<Lab>(() => api.release(labId, version), [labId, version]);
  const [variant, setVariant] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    if (lab.data && !variant) setVariant(lab.data.variants[0]?.id ?? "");
  }, [lab.data, variant]);

  async function start() {
    setBusy(true);
    setError(undefined);
    try {
      const s: LabSession = await api.start(labId, version, variant);
      go(`/sessions/${s.sessionId}`);
    } catch (e) {
      if (e instanceof ApiError && e.code === "SESSION_ALREADY_ACTIVE") {
        const mine = await api.sessions();
        const active = mine.items.find((s) => s.labId === labId && s.version === version);
        if (active) return go(`/sessions/${active.sessionId}`);
      }
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  if (lab.loading) return <main className="page muted">Carregando…</main>;
  if (lab.error || !lab.data) return <main className="page"><ErrorBox message={lab.error ?? "Não encontrado"} /></main>;
  const l = lab.data;
  return (
    <main className="page narrow">
      <a className="back" href="#/">← Laboratórios</a>
      <p className="eyebrow">
        {l.labId} · versão {l.version} · {l.primaryCwe}
      </p>
      <h1>{l.title}</h1>
      <section className="card story">
        <h2>Sua missão</h2>
        <dl>
          <dt>Papel</dt>
          <dd>{l.learning.story.role}</dd>
          <dt>Aplicação</dt>
          <dd>{l.learning.story.application}</dd>
          <dt>Contexto</dt>
          <dd>{l.learning.story.context}</dd>
          <dt>Missão</dt>
          <dd>{l.learning.story.mission}</dd>
        </dl>
      </section>
      <section className="two-col">
        <div className="card">
          <h2>Objetivos</h2>
          <ul>
            {l.learning.objectives.map((o) => (
              <li key={o}>{o}</li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h2>Etapas</h2>
          <ol className="steps-preview">
            {l.steps.map((s) => (
              <li key={s.id}>
                {s.title} <span className="muted small">· {s.points} pts</span>
              </li>
            ))}
          </ol>
        </div>
      </section>
      <section className="card start">
        <label htmlFor="variant">Linguagem / stack</label>
        <select id="variant" value={variant} onChange={(e) => setVariant(e.target.value)}>
          {l.variants.map((v) => (
            <option key={v.id} value={v.id}>
              {v.language} · {v.framework} ({v.ttlMinutes} min)
            </option>
          ))}
        </select>
        <button className="primary big" onClick={start} disabled={busy || !variant}>
          {busy ? "Iniciando…" : "Iniciar laboratório"}
        </button>
        <p className="muted small">
          A sessão cria um ambiente exclusivo e temporário, encerrado automaticamente ao fim do prazo.
        </p>
        {error && <ErrorBox message={error} />}
      </section>
    </main>
  );
}

export function StatusChip({ status }: { status: string }) {
  const labels: Record<string, string> = {
    REQUESTED: "Solicitada",
    PROVISIONING: "Preparando ambiente",
    READY: "Pronta",
    ACTIVE: "Em uso",
    TERMINATING: "Encerrando",
    TERMINATED: "Encerrada",
    EXPIRED: "Expirada",
    FAILED: "Falhou",
    COMPLETED: "Concluída",
  };
  return <span className={`chip chip-${status.toLowerCase()}`}>{labels[status] ?? status}</span>;
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="error" role="alert">
      {message}
    </div>
  );
}
