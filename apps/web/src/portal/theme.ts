/**
 * Aparência do portal (ADR-026): quatro modos escolhidos pelo usuário e salvos no perfil (backend).
 * "Automático" (padrão) segue o tema do sistema: claro ou tudo escuro.
 * O modo também fica em cache local para a página já abrir com as cores certas.
 * As aplicações dos laboratórios não mudam: rodam em outra origem, com as próprias cores.
 */
import { useSyncExternalStore } from "react";

export type Tema = "auto" | "claro" | "codigo" | "escuro";
/** O que de fato vai em ``data-tema`` (portal e workspace). */
export type TemaEfetivo = Exclude<Tema, "auto">;

export const TEMAS: { id: Tema; nome: string; desc: string }[] = [
  { id: "auto", nome: "Automático", desc: "Segue o tema do sistema: claro ou tudo escuro." },
  { id: "claro", nome: "Claro", desc: "Portal e editor claros." },
  { id: "codigo", nome: "Código escuro", desc: "Portal claro; editor e lista de arquivos escuros, como numa IDE." },
  { id: "escuro", nome: "Tudo escuro", desc: "Portal, etapas e editor escuros." },
];

const CACHE = "cecyber.tema";
const listeners = new Set<() => void>();
let atual: Tema = lerCache();

export function isTema(v: unknown): v is Tema {
  return v === "auto" || v === "claro" || v === "codigo" || v === "escuro";
}

function lerCache(): Tema {
  try {
    const v = localStorage.getItem(CACHE);
    return isTema(v) ? v : "auto";
  } catch {
    return "auto";
  }
}

const sistemaEscuro =
  typeof window !== "undefined" && typeof window.matchMedia === "function"
    ? window.matchMedia("(prefers-color-scheme: dark)")
    : null;

function resolver(t: Tema): TemaEfetivo {
  if (t !== "auto") return t;
  return sistemaEscuro?.matches ? "escuro" : "claro";
}

/** Aplica o modo no documento do portal: ``data-tema`` troca os tokens de cor em styles.css. */
export function aplicarTema(t: Tema): void {
  atual = t;
  document.documentElement.dataset.tema = resolver(t);
  try {
    localStorage.setItem(CACHE, t);
  } catch {
    /* sem armazenamento local: vale até recarregar */
  }
  listeners.forEach((l) => l());
}

export function temaAtual(): Tema {
  return atual;
}

const assinar = (l: () => void) => (listeners.add(l), () => listeners.delete(l));

/** Modo escolhido (para o menu). */
export function useTema(): Tema {
  return useSyncExternalStore(assinar, () => atual);
}

/** Modo aplicado de fato, já resolvendo "Automático" pelo sistema (para repassar ao workspace). */
export function useTemaEfetivo(): TemaEfetivo {
  return useSyncExternalStore(assinar, () => resolver(atual));
}

sistemaEscuro?.addEventListener?.("change", () => {
  if (atual === "auto") aplicarTema("auto");
});

aplicarTema(atual);
