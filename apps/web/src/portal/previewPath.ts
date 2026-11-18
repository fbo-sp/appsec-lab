/** Normaliza o que o aluno digitou para um caminho da própria aplicação (nunca outra origem). */
export function previewPathFrom(input: string, origin: string): string {
  const raw = input.trim() || "/";
  try {
    const url = new URL(raw.startsWith("/") ? raw : `/${raw}`, origin);
    if (url.origin !== origin) return "/";
    return `${url.pathname}${url.search}${url.hash}`;
  } catch {
    return "/";
  }
}
