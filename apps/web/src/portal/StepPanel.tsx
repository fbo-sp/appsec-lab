// Painel de etapas: progresso, validação (resposta ou comportamento) e dicas.
// O backend decide desbloqueio, aprovação e pontos; a interface só exibe e solicita.
import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError, type Evaluation, type Progress, type Step } from "./api";

const PENDING = new Set(["QUEUED", "RUNNING"]);
const STATUS_LABEL: Record<Evaluation["status"], string> = {
  QUEUED: "Na fila de validação…",
  RUNNING: "Validando sua aplicação…",
  PASSED: "Etapa concluída",
  FAILED: "Ainda não",
  ERROR: "Falha técnica na validação",
};

function message(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

export function StepPanel({
  sessionId,
  onExit,
  onProgress,
  onShowLog,
}: {
  sessionId: string;
  onExit: () => void;
  onProgress?: () => void;
  onShowLog?: () => void;
}) {
  const onProgressRef = useRef(onProgress);
  onProgressRef.current = onProgress;
  const [progress, setProgress] = useState<Progress>();
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [selected, setSelected] = useState<string>();
  const [error, setError] = useState<string>();

  const reload = useCallback(async (selectNext = false) => {
    try {
      const p = await api.steps(sessionId);
      setProgress((prev) => {
        // Abre o resumo ao concluir (ou ao reabrir uma sessão de tentativa já concluída).
        if (p.attempt.status === "COMPLETED" && prev?.attempt.status !== "COMPLETED") setSummaryOpen(true);
        return p;
      });
      setError(undefined);
      onProgressRef.current?.();
      const current = p.items.find((s) => s.status === "AVAILABLE");
      setSelected((old) => (selectNext || !old ? (current ?? p.items[p.items.length - 1])?.id : old));
    } catch (e) {
      setError(message(e));
    }
  }, [sessionId]);

  useEffect(() => {
    reload();
  }, [reload]);

  if (!progress) return <div className="muted">{error ?? "Carregando etapas…"}</div>;
  const { attempt, items } = progress;
  const step = items.find((s) => s.id === selected);
  const pct = Math.min(100, Math.round((attempt.score / Math.max(1, attempt.passingScore)) * 100));

  return (
    <>
      <div className="score" aria-label="Pontuação">
        <div className="score-row">
          <strong>Pontuação</strong>
          <span>
            {attempt.score} / {attempt.passingScore} pts
          </span>
        </div>
        <div className="meter" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <span style={{ width: `${pct}%` }} />
        </div>
        {attempt.status === "COMPLETED" && (
          <div className="completed">
            🎉 Laboratório concluído!{" "}
            <button className="link" onClick={() => setSummaryOpen(true)}>
              ver resumo
            </button>
          </div>
        )}
      </div>
      <h2>Etapas</h2>
      <ol>
        {items.map((s) => (
          <li key={s.id}>
            <button
              className={`step step-${s.status.toLowerCase()} ${s.id === selected ? "step-selected" : ""}`}
              onClick={() => s.status !== "LOCKED" && setSelected(s.id)}
              disabled={s.status === "LOCKED"}
              title={s.status === "LOCKED" ? "Conclua a etapa anterior" : undefined}
            >
              <span className="step-n">{s.status === "PASSED" ? "✓" : s.order}</span>
              <span className="step-name">
                {s.title}
                <span className="muted small">
                  {" "}
                  · {s.status === "PASSED" ? `${s.pointsAwarded}/` : ""}
                  {s.points} pts
                </span>
              </span>
              {s.status === "LOCKED" && <span className="lock">🔒</span>}
            </button>
          </li>
        ))}
      </ol>
      {error && <div className="error">{error}</div>}
      {step && step.status !== "LOCKED" && (
        <StepDetail key={step.id} sessionId={sessionId} step={step} onChanged={reload} onShowLog={onShowLog} />
      )}
      {summaryOpen && attempt.status === "COMPLETED" && (
        <Summary progress={progress} onClose={() => setSummaryOpen(false)} onExit={onExit} />
      )}
    </>
  );
}

function StepDetail({
  sessionId,
  step,
  onChanged,
  onShowLog,
}: {
  sessionId: string;
  step: Step;
  onChanged: (selectNext?: boolean) => Promise<void>;
  onShowLog?: () => void;
}) {
  const [hintsOpen, setHintsOpen] = useState(false);
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState<Evaluation | null>(step.lastSubmission ?? null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();
  const [hintBusy, setHintBusy] = useState(false);
  const passed = step.status === "PASSED";
  const kind = step.validation?.type;

  // Acompanha uma validação pendente (o worker avalia fora do workspace).
  useEffect(() => {
    if (!evaluation || !PENDING.has(evaluation.status)) return;
    const t = setTimeout(async () => {
      try {
        const ev = await api.evaluation(sessionId, evaluation.evaluationId);
        setEvaluation(ev);
        if (!PENDING.has(ev.status)) await onChanged(ev.status === "PASSED");
      } catch (e) {
        setError(message(e));
      }
    }, 1000);
    return () => clearTimeout(t);
  }, [evaluation, sessionId, onChanged]);

  async function validate(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(undefined);
    try {
      const ev = await api.evaluate(sessionId, step.id, kind === "answer" ? answer : undefined);
      setEvaluation(ev);
      if (!PENDING.has(ev.status)) await onChanged(ev.status === "PASSED");
    } catch (err) {
      setError(err instanceof ApiError && err.code === "EVALUATION_IN_PROGRESS" ? "Já há uma validação em andamento." : message(err));
    } finally {
      setBusy(false);
    }
  }

  async function reveal(level: number) {
    setHintBusy(true);
    setError(undefined);
    try {
      await api.revealHint(sessionId, step.id, level);
      await onChanged();
    } catch (err) {
      setError(message(err));
    } finally {
      setHintBusy(false);
    }
  }

  const hints = step.hints ?? { available: 0, revealed: [] };
  const nextHint = hints.revealed.length + 1;
  const pending = evaluation !== null && PENDING.has(evaluation.status);
  const hintButton = (
    <button type="button" className="hint-button" onClick={() => setHintsOpen(true)}>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M9 18h6" />
        <path d="M10 22h4" />
        <path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2V17h6v-.3c0-.8.4-1.5 1-2A7 7 0 0 0 12 2z" />
      </svg>
      Dicas ({hints.revealed.length}/{hints.available})
    </button>
  );

  return (
    <div className="step-detail">
      <h3>{step.title}</h3>
      <p>{step.explanation}</p>
      <h4>Tarefa</h4>
      <p>{step.task}</p>
      <h4>Conceito</h4>
      <p>{step.concept}</p>

      <h4>Validação</h4>
      {passed && evaluation?.status === "PASSED" ? null : passed ? (
        <div className="result result-passed">
          ✓ Etapa concluída · {step.pointsAwarded} pts
        </div>
      ) : kind === "unavailable" ? (
        <div className="result result-error">O validador desta etapa não está disponível.</div>
      ) : (
        <form className="validate" onSubmit={validate}>
          {kind === "answer" && (
            <label>
              <span className="small">{step.validation?.answerPrompt}</span>
              <input
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                maxLength={500}
                placeholder="Sua resposta"
                autoComplete="off"
                required
              />
            </label>
          )}
          {kind === "http" && (
            <p className="muted small">
              Salve seus arquivos no editor. A validação copia o workspace e testa sua aplicação num ambiente
              separado, sem acesso ao seu editor.
            </p>
          )}
          <div className="validate-actions">
            <button className="primary" type="submit" disabled={busy || pending}>
              {pending ? "Validando…" : "Validar"}
            </button>
            {hints.available > 0 && hintButton}
          </div>
        </form>
      )}
      {(passed || kind === "unavailable") && hints.available > 0 && <div className="validate-actions">{hintButton}</div>}

      {evaluation && !(passed && evaluation.status !== "PASSED") && (
        <div className={`result result-${evaluation.status.toLowerCase()}`} aria-live="polite">
          <strong>{STATUS_LABEL[evaluation.status]}</strong>
          {evaluation.criteria.length > 0 && (
            <ul className="criteria">
              {evaluation.criteria.map((c) => (
                <li key={c.id} className={c.passed ? "ok" : "fail"}>
                  {c.passed ? "✓" : "✗"} {c.description}
                </li>
              ))}
            </ul>
          )}
          {evaluation.feedback && <p>{evaluation.feedback}</p>}
          {onShowLog && !PENDING.has(evaluation.status) && (
            <button className="link result-link" onClick={onShowLog}>
              ver histórico na aba Validação
            </button>
          )}
        </div>
      )}
      {step.submissions > 0 && <p className="muted small">Tentativas nesta etapa: {step.submissions} (sem limite)</p>}
      {error && <div className="error">{error}</div>}

      {hintsOpen && (
        <HintsModal
          stepTitle={step.title}
          hints={hints}
          busy={hintBusy}
          error={error}
          onReveal={() => reveal(nextHint)}
          onClose={() => setHintsOpen(false)}
        />
      )}
    </div>
  );
}

function HintsModal({
  stepTitle,
  hints,
  busy,
  error,
  onReveal,
  onClose,
}: {
  stepTitle: string;
  hints: { available: number; revealed: { level: number; text: string }[] };
  busy: boolean;
  error?: string;
  onReveal: () => void;
  onClose: () => void;
}) {
  const next = hints.revealed.length + 1;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="card hints-modal" role="dialog" aria-modal="true" aria-labelledby="hints-title">
        <div className="hints-head">
          <div>
            <h2 id="hints-title">Dicas · {stepTitle}</h2>
            <p className="muted small">Revele uma de cada vez. Dicas não descontam pontos.</p>
          </div>
          <button className="icon-close" aria-label="Fechar dicas" onClick={onClose}>
            ×
          </button>
        </div>
        {hints.revealed.map((h) => (
          <div key={h.level} className="hint">
            <span className="hint-n">Dica {h.level}</span>
            <span>{h.text}</span>
          </div>
        ))}
        {next <= hints.available ? (
          <div className="hint-locked">
            <span className="muted">
              {hints.revealed.length === 0 ? "Nenhuma dica revelada ainda." : `Dica ${next} ainda oculta.`}
            </span>
            <button className="primary" onClick={onReveal} disabled={busy} autoFocus>
              {busy ? "Revelando…" : `Revelar dica ${next}`}
            </button>
          </div>
        ) : (
          <p className="muted small">Todas as dicas desta etapa já foram reveladas.</p>
        )}
        {error && <div className="error">{error}</div>}
        <div className="summary-actions">
          <button onClick={onClose}>Voltar ao laboratório</button>
        </div>
      </div>
    </div>
  );
}

function duration(fromIso: string, toIso: string): string {
  const total = Math.max(0, Math.round((Date.parse(toIso) - Date.parse(fromIso)) / 1000));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const sec = total % 60;
  if (h) return `${h} h ${m} min`;
  if (m) return `${m} min ${sec} s`;
  return `${sec} s`;
}

function Summary({ progress, onClose, onExit }: { progress: Progress; onClose: () => void; onExit: () => void }) {
  const { attempt, items } = progress;
  const [leaving, setLeaving] = useState(false);
  const elapsedSec = (Date.parse(attempt.completedAt ?? attempt.startedAt) - Date.parse(attempt.startedAt)) / 1000;
  const firstTry = items.filter((s) => s.submissions === 1).length;
  const badges = [
    attempt.hintsUsed === 0 && { icon: "🧠", title: "Sem dicas", text: "Concluiu sem revelar nenhuma dica." },
    firstTry === items.length && { icon: "🎯", title: "Precisão", text: "Todas as etapas validadas na primeira tentativa." },
    elapsedSec < 10 * 60 && { icon: "⚡", title: "Rápido", text: "Concluiu em menos de 10 minutos." },
    attempt.hintsUsed > 0 && { icon: "🔎", title: "Investigador", text: "Usou dicas para destravar o caminho." },
  ].filter(Boolean) as { icon: string; title: string; text: string }[];

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-labelledby="summary-title">
      <div className="summary card">
        <div className="summary-hero">
          <div className="trophy" aria-hidden="true">🏆</div>
          <h2 id="summary-title">Laboratório concluído!</h2>
          <p className="muted">Você completou todas as etapas. Veja como foi:</p>
        </div>
        <div className="stats">
          <div className="stat">
            <span className="stat-value">
              {attempt.score}
              <small>/{attempt.maxScore}</small>
            </span>
            <span className="stat-label">pontos</span>
          </div>
          <div className="stat">
            <span className="stat-value">{duration(attempt.startedAt, attempt.completedAt ?? attempt.startedAt)}</span>
            <span className="stat-label">tempo total</span>
          </div>
          <div className="stat">
            <span className="stat-value">{attempt.hintsUsed}</span>
            <span className="stat-label">{attempt.hintsUsed === 1 ? "dica usada" : "dicas usadas"}</span>
          </div>
          <div className="stat">
            <span className="stat-value">{attempt.submissions}</span>
            <span className="stat-label">{attempt.submissions === 1 ? "validação" : "validações"}</span>
          </div>
        </div>
        {badges.length > 0 && (
          <div className="badges">
            {badges.map((b) => (
              <div key={b.title} className="badge" title={b.text}>
                <span aria-hidden="true">{b.icon}</span>
                <span>
                  <strong>{b.title}</strong>
                  <span className="muted small">{b.text}</span>
                </span>
              </div>
            ))}
          </div>
        )}
        <table className="summary-table">
          <thead>
            <tr>
              <th>Etapa</th>
              <th>Pontos</th>
              <th>Tentativas</th>
              <th>Dicas</th>
            </tr>
          </thead>
          <tbody>
            {items.map((s) => (
              <tr key={s.id}>
                <td>
                  <span className="ok">✓</span> {s.title}
                </td>
                <td>
                  {s.pointsAwarded}/{s.points}
                </td>
                <td>{s.submissions}</td>
                <td>{s.hints?.revealed.length ?? 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted small">
          Ao voltar ao painel, este ambiente é encerrado e os arquivos temporários são descartados. Seu resultado
          continua registrado.
        </p>
        <div className="summary-actions">
          <button className="link" onClick={onClose}>
            Continuar explorando
          </button>
          <button
            className="primary"
            disabled={leaving}
            onClick={() => {
              setLeaving(true);
              onExit();
            }}
            autoFocus
          >
            {leaving ? "Encerrando…" : "Voltar ao painel"}
          </button>
        </div>
      </div>
    </div>
  );
}
