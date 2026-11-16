import { describe, expect, it } from "vitest";
import type { Lab } from "./api";
import { matchesFilter } from "./catalogFilter";

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
});
