/**
 * Aparência do portal (ADR-026): três modos escolhidos pelo usuário e salvos no perfil (backend).
 * O modo também fica em cache local para a página já abrir com as cores certas.
 * As aplicações dos laboratórios não mudam: rodam em outra origem, com as próprias cores.
 */
import { useSyncExternalStore } from "react";

export type Tema = "claro" | "codigo" | "escuro";

export const TEMAS: { id: Tema; nome: string; desc: string }[] = [
  { id: "claro", nome: "Claro", desc: "Portal e editor claros." },
  { id: "codigo", nome: "Código escuro", desc: "Portal claro; editor e lista de arquivos escuros, como numa IDE." },
  { id: "escuro", nome: "Tudo escuro", desc: "Portal, etapas e editor escuros." },
];

const CACHE = "cecyber.tema";
const listeners = new Set<() => void>();
let atual: Tema = lerCache();

export function isTema(v: unknown): v is Tema {
  return v === "claro" || v === "codigo" || v === "escuro";
}

function lerCache(): Tema {
  try {
    const v = localStorage.getItem(CACHE);
    return isTema(v) ? v : "claro";
  } catch {
    return "claro";
  }
}

/** Aplica o modo no documento do portal: ``data-tema`` troca os tokens de cor em styles.css. */
export function aplicarTema(t: Tema): void {
  atual = t;
  document.documentElement.dataset.tema = t;
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

export function useTema(): Tema {
  return useSyncExternalStore(
    (l) => (listeners.add(l), () => listeners.delete(l)),
    () => atual,
  );
}

aplicarTema(atual);
