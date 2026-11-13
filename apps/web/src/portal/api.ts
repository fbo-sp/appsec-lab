// Cliente da API do plano de controle. Em modo local a identidade vem de cabeçalhos de
// desenvolvimento (X-Dev-User), aceitos pelo backend somente com APP_ENV=local|test.

export type Lab = {
  labId: string;
  version: string;
  title: string;
  primaryCwe: string;
  learning: {
    difficulty: string;
    estimatedMinutes: number;
    objectives: string[];
    story: { role: string; application: string; context: string; mission: string };
  };
  variants: { id: string; language: string; framework: string; ttlMinutes: number }[];
  steps: { id: string; order: number; title: string; points: number }[];
};

export type LabSession = {
  sessionId: string;
  status: string;
  labId: string;
  version: string;
  variantId: string;
  expiresAt: string;
  lastErrorCode: string | null;
  ttlMinutes: number;
  renewals: number;
  maxRenewals: number;
  renewableAt: string | null;
};

export type Criterion = { id: string; description: string; passed: boolean };

export type Evaluation = {
  evaluationId: string;
  status: "QUEUED" | "RUNNING" | "PASSED" | "FAILED" | "ERROR";
  criteria: Criterion[];
  feedback: string | null;
  createdAt: string;
  finishedAt: string | null;
};

export type Step = {
  id: string;
  order: number;
  title: string;
  points: number;
  status: "AVAILABLE" | "LOCKED" | "PASSED";
  pointsAwarded: number;
  submissions: number;
  explanation?: string;
  task?: string;
  concept?: string | null;
  references?: Reference[];
  validation?: { type: "answer" | "http" | "unavailable"; answerPrompt: string | null };
  hints?: Hints;
  lastSubmission?: Evaluation | null;
};

export type Reference = { title: string; url: string };

/** Dicas da etapa; ``cost``/``nextCost`` em pontos inteiros (ADR-013). */
export type Hints = { available: number; revealed: { level: number; text: string; cost?: number }[]; nextCost?: number };

export type Progress = {
  sessionId: string;
  attempt: {
    id: string;
    status: "IN_PROGRESS" | "COMPLETED";
    score: number;
    maxScore: number;
    earnedPoints?: number;
    hintPenalty?: number;
    hintPenaltyCap?: number;
    passingScore: number;
    startedAt: string;
    completedAt: string | null;
    hintsUsed: number;
    submissions: number;
  };
  items: Step[];
  wrapUp?: { text: string; references?: Reference[] } | null;
};

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}

const USER_KEY = "cecyber.devUser";

export function currentUser(): string | null {
  try {
    return localStorage.getItem(USER_KEY);
  } catch {
    return null;
  }
}

export function setUser(user: string | null): void {
  try {
    if (user) localStorage.setItem(USER_KEY, user);
    else localStorage.removeItem(USER_KEY);
  } catch {
    /* armazenamento indisponível: identidade dura só até recarregar */
  }
}

async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
  const user = currentUser();
  const headers = new Headers(init.headers);
  if (user) headers.set("X-Dev-User", user);
  if (init.body) headers.set("Content-Type", "application/json");
  const res = await fetch(path, { ...init, headers });
  const body = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const err = body?.error ?? {};
    throw new ApiError(res.status, err.code ?? "ERROR", err.message ?? `Erro HTTP ${res.status}`);
  }
  return body as T;
}

export const api = {
  labs: () => call<{ items: Lab[] }>("/api/v1/labs"),
  release: (labId: string, version: string) => call<Lab>(`/api/v1/labs/${labId}/releases/${version}`),
  sessions: () => call<{ items: LabSession[] }>("/api/v1/sessions"),
  session: (id: string) => call<LabSession>(`/api/v1/sessions/${id}`),
  steps: (id: string) => call<Progress>(`/api/v1/sessions/${id}/steps`),
  evaluate: (id: string, stepId: string, answer?: string) =>
    call<Evaluation>(`/api/v1/sessions/${id}/steps/${stepId}/evaluations`, {
      method: "POST",
      headers: { "Idempotency-Key": `ui-${crypto.randomUUID()}` },
      body: JSON.stringify(answer === undefined ? {} : { answer }),
    }),
  evaluations: (id: string) =>
    call<{ items: (Evaluation & { stepId: string; stepTitle: string; stepOrder: number })[] }>(
      `/api/v1/sessions/${id}/evaluations`,
    ),
  evaluation: (id: string, evaluationId: string) =>
    call<Evaluation>(`/api/v1/sessions/${id}/evaluations/${evaluationId}`),
  revealHint: (id: string, stepId: string, level: number) =>
    call<{ level: number; text: string; penalty: number; score?: number }>(
      `/api/v1/sessions/${id}/steps/${stepId}/hints/${level}/reveal`,
      { method: "POST" },
    ),
  start: (labId: string, version: string, variantId: string) =>
    call<LabSession>("/api/v1/sessions", {
      method: "POST",
      headers: { "Idempotency-Key": `ui-${crypto.randomUUID()}` },
      body: JSON.stringify({ labId, version, variantId }),
    }),
  renew: (id: string) => call<LabSession>(`/api/v1/sessions/${id}/renewals`, { method: "POST" }),
  terminate: (id: string) => call<LabSession>(`/api/v1/sessions/${id}`, { method: "DELETE" }),
  ticket: (id: string, purpose: "workspace" | "preview") =>
    call<{ url: string }>(`/api/v1/sessions/${id}/gateway-ticket`, {
      method: "POST",
      body: JSON.stringify({ purpose }),
    }),
};
