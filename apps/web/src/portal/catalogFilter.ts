import type { Lab } from "./api";

/** CWE-1000 (raiz da visão "Research Concepts") marca um lab sem vulnerabilidade: o tutorial (ADR-018). */
export function isTutorial(lab: Lab): boolean {
  return lab.primaryCwe === "CWE-1000";
}

export const SECTORS: Record<string, string> = {
  financeiro: "Financeiro",
  saude: "Saúde",
  "industria-energia": "Indústria e energia",
};
export const MODULES: Record<string, string> = {
  foundation: "Foundation",
  trained: "Trained",
  expert: "Expert",
  master: "Master",
};

export function readPref(key: string): string {
  try {
    return localStorage.getItem(key) ?? "";
  } catch {
    return "";
  }
}

export function writePref(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Sem armazenamento local (janela privada): o filtro só não é lembrado.
  }
}

/** Filtro do painel por ramo e módulo (ADR-021). O tutorial aparece sempre. */
export function matchesFilter(lab: Lab, sector: string, module: string): boolean {
  if (isTutorial(lab)) return true;
  if (sector && !(lab.sectors ?? []).includes(sector)) return false;
  if (module && !(lab.courseModules ?? []).includes(module)) return false;
  return true;
}
