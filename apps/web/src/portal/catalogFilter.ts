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
/** Listas de classificação para o filtro (ADR-021). A chave é o ``framework`` do manifesto. */
export const FRAMEWORKS: Record<string, string> = {
  "OWASP Top 10": "OWASP Top 10 (Web)",
  "OWASP API Security Top 10": "OWASP API Security Top 10",
  "SANS CWE Top 25": "SANS CWE Top 25",
  "OWASP Mobile Top 10": "OWASP Mobile Top 10",
  "OWASP MASVS": "OWASP MASVS",
};

/** Uma entrada "Não se enquadra; use o CWE" não conta como pertencer à lista. */
function entradaReal(entry: string): boolean {
  return !/n[ãa]o se enquadra/i.test(entry);
}

/** Listas (frameworks) às quais o lab efetivamente pertence (com ao menos uma entrada real). */
export function labFrameworks(lab: Lab): string[] {
  const listas = new Set<string>();
  for (const c of lab.classifications ?? []) {
    if ((c.entries ?? []).some(entradaReal)) listas.add(c.framework);
  }
  return [...listas];
}

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

/** Filtro do painel por ramo, módulo e classificação (ADR-021). O tutorial aparece sempre. */
export function matchesFilter(lab: Lab, sector: string, module: string, framework = ""): boolean {
  if (isTutorial(lab)) return true;
  if (sector && !(lab.sectors ?? []).includes(sector)) return false;
  if (module && !(lab.courseModules ?? []).includes(module)) return false;
  if (framework && !labFrameworks(lab).includes(framework)) return false;
  return true;
}
