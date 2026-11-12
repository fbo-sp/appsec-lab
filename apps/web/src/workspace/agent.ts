// Chamadas ao agente de workspace via gateway (mesma origem). O cabeçalho próprio força preflight CORS
// em requisições vindas de outras origens, que o gateway nunca autoriza (proteção contra CSRF).
const BASE = "./__cecyber/api";
const HEADERS = { "X-Cecyber-Workspace": "1" };

export type Entry = { name: string; path: string; type: "file" | "dir"; size: number | null };

async function req(url: string, init: RequestInit = {}): Promise<Response> {
  const res = await fetch(url, { ...init, credentials: "same-origin", headers: { ...HEADERS, ...init.headers } });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    let msg = text;
    try {
      msg = JSON.parse(text)?.error?.message ?? text;
    } catch {
      /* texto puro */
    }
    throw new Error(msg || `Erro HTTP ${res.status}`);
  }
  return res;
}

export async function listDir(path = ""): Promise<Entry[]> {
  const res = await req(`${BASE}/files?path=${encodeURIComponent(path)}`);
  return (await res.json()).entries;
}

export async function readFile(path: string): Promise<string> {
  const res = await req(`${BASE}/file?path=${encodeURIComponent(path)}`);
  return (await res.json()).content;
}

export async function writeFile(path: string, content: string): Promise<void> {
  await req(`${BASE}/file?path=${encodeURIComponent(path)}`, { method: "PUT", body: content });
}

export function terminalUrl(): string {
  const u = new URL("./__cecyber/term", location.href);
  u.protocol = u.protocol === "https:" ? "wss:" : "ws:";
  return u.toString();
}
