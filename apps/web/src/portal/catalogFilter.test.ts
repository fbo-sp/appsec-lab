import { describe, expect, it } from "vitest";
import type { Lab } from "./api";
import { labFrameworks, matchesFilter } from "./catalogFilter";

function lab(over: Partial<Lab>): Lab {
  return {
    labId: "LAB-005",
    version: "1.0.0",
    title: "t",
    primaryCwe: "CWE-79",
    secondaryCwes: [],
    learning: {
      difficulty: "beginner",
      estimatedMinutes: 30,
      objectives: [],
      story: { role: "", application: "", context: "", mission: "" },
    },
    variants: [],
    steps: [],
    ...over,
  };
}

describe("matchesFilter (ADR-021)", () => {
  const fin = lab({ sectors: ["financeiro"], courseModules: ["trained", "master"] });
  const antigo = lab({ labId: "LAB-001" });
  const tutorial = lab({ labId: "LAB-000", primaryCwe: "CWE-1000" });

  it("sem filtro mostra tudo", () => {
    expect([fin, antigo, tutorial].every((l) => matchesFilter(l, "", ""))).toBe(true);
  });
  it("filtra por ramo e por módulo", () => {
    expect(matchesFilter(fin, "financeiro", "")).toBe(true);
    expect(matchesFilter(fin, "saude", "")).toBe(false);
    expect(matchesFilter(fin, "", "master")).toBe(true);
    expect(matchesFilter(fin, "financeiro", "foundation")).toBe(false);
  });
  it("lab sem ramo some com filtro, mas o tutorial aparece sempre", () => {
    expect(matchesFilter(antigo, "financeiro", "")).toBe(false);
    expect(matchesFilter(tutorial, "saude", "expert")).toBe(true);
  });

  const api = lab({
    classifications: [
      { framework: "OWASP Top 10", edition: "2025", entries: ["A01 Broken Access Control"] },
      { framework: "OWASP API Security Top 10", edition: "2023", entries: ["API1 BOLA"] },
      { framework: "SANS CWE Top 25", edition: "2025", entries: ["Não se enquadra; use o CWE"] },
    ],
  });
  it("filtra por classificação (framework)", () => {
    expect(matchesFilter(api, "", "", "OWASP API Security Top 10")).toBe(true);
    expect(matchesFilter(api, "", "", "OWASP Top 10")).toBe(true);
    expect(matchesFilter(fin, "", "", "OWASP API Security Top 10")).toBe(false);
  });
  it('"Não se enquadra" não conta como pertencer à lista', () => {
    expect(labFrameworks(api)).toEqual(["OWASP Top 10", "OWASP API Security Top 10"]);
    expect(matchesFilter(api, "", "", "SANS CWE Top 25")).toBe(false);
  });
  it("reconhece as listas mobile (ADR-025)", () => {
    const mob = lab({
      classifications: [
        { framework: "OWASP Mobile Top 10", edition: "2024", entries: ["M9 Insecure Data Storage"] },
        { framework: "OWASP MASVS", edition: "2023", entries: ["MASVS-STORAGE-1"] },
      ],
    });
    expect(matchesFilter(mob, "", "", "OWASP Mobile Top 10")).toBe(true);
    expect(matchesFilter(mob, "", "", "OWASP MASVS")).toBe(true);
    expect(matchesFilter(api, "", "", "OWASP Mobile Top 10")).toBe(false);
  });
  it("classificação combina com os outros filtros e o tutorial ignora tudo", () => {
    expect(matchesFilter(api, "", "", "")).toBe(true);
    expect(matchesFilter(tutorial, "", "", "OWASP API Security Top 10")).toBe(true);
  });
});
