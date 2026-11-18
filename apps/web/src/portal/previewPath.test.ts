import { describe, expect, it } from "vitest";
import { previewPathFrom } from "./previewPath";

const ORIGIN = "http://127.0.0.1:8002";

describe("previewPathFrom", () => {
  it("mantém caminhos da aplicação, com consulta", () => {
    expect(previewPathFrom("/comprovantes/10457", ORIGIN)).toBe("/comprovantes/10457");
    expect(previewPathFrom(" api/comprovantes/1?x=2 ", ORIGIN)).toBe("/api/comprovantes/1?x=2");
    expect(previewPathFrom("", ORIGIN)).toBe("/");
  });

  it("nunca navega para outra origem", () => {
    expect(previewPathFrom("//exemplo.example/x", ORIGIN)).toBe("/");
    expect(previewPathFrom("https://exemplo.example/", ORIGIN)).toBe("/https://exemplo.example/");
  });
});
