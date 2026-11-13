// Aba Validação: histórico de validações da tentativa (mais recentes primeiro).
import { useEffect, useState } from "react";
import { api, type Evaluation } from "./api";

type Item = Evaluation & { stepId: string; stepTitle: string; stepOrder: number };

const LABEL: Record<Evaluation["status"], string> = {
  QUEUED: "Na fila",
  RUNNING: "Validando",
  PASSED: "Concluída",
  FAILED: "Ainda não",
  ERROR: "Falha técnica",
};

function seconds(a: string, b: string | null): string {
  if (!b) return "";
  const s = Math.max(0, Math.round((Date.parse(b) - Date.parse(a)) / 1000));
  return ` · ${s} s`;
}

export function ValidationLog({ sessionId, version }: { sessionId: string; version: number }) {
  const [items, setItems] = useState<Item[]>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    let stop = false;
    let timer: ReturnType<typeof setTimeout>;
    const load = async () => {
      try {
        const r = await api.evaluations(sessionId);
        if (stop) return;
        setItems(r.items);
        setError(undefined);
        // Enquanto houver validação pendente, atualiza sozinho.
        if (r.items.some((i) => i.status === "QUEUED" || i.status === "RUNNING")) timer = setTimeout(load, 1500);
      } catch (e) {
        if (!stop) setError(e instanceof Error ? e.message : String(e));
      }
    };
    load();
    return () => {
      stop = true;
      clearTimeout(timer);
    };
  }, [sessionId, version]);

  return (
    <div className="vlog" role="tabpanel" aria-label="Histórico de validação">
      <h2>Histórico de validação</h2>
      {error && <div className="error">{error}</div>}
      {!items ? (
        <p className="muted">Carregando…</p>
      ) : items.length === 0 ? (
        <p className="muted">Nenhuma validação ainda. Use o botão Validar na etapa atual.</p>
      ) : (
        <ol className="vlog-list">
          {items.map((i) => (
            <li key={i.evaluationId} className={`vlog-item vlog-${i.status.toLowerCase()}`}>
              <div className="vlog-head">
                <strong>
                  Etapa {i.stepOrder} · {i.stepTitle} · {LABEL[i.status]}
                </strong>
                <span className="muted small">
                  {new Date(i.createdAt).toLocaleTimeString("pt-BR")}
                  {seconds(i.createdAt, i.finishedAt)}
                </span>
              </div>
              {i.criteria.length > 0 && (
                <ul className="criteria">
                  {i.criteria.map((c) => (
                    <li key={c.id} className={c.passed ? "ok" : "fail"}>
                      {c.passed ? "✓" : "✗"} {c.description}
                    </li>
                  ))}
                </ul>
              )}
              {i.feedback && <p className="small">{i.feedback}</p>}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
