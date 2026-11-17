import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import { aplicarTema, isTema, TEMAS, useTema, type Tema } from "./theme";

/** Miniatura do modo: faixa da esquerda = etapas/portal, direita = área de código. */
const MINI: Record<Tema, [string, string]> = {
  claro: ["#f3f5f8", "#ffffff"],
  codigo: ["#f3f5f8", "#161a22"],
  escuro: ["#12151c", "#1b2029"],
};

/** Botão "Aparência" no cabeçalho (ADR-026). Carrega e salva o modo no perfil do usuário. */
export function Aparencia({ user }: { user: string }) {
  const tema = useTema();
  const [open, setOpen] = useState(false);
  const [erro, setErro] = useState<string>();
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let vivo = true;
    api
      .preferences()
      .then((p) => vivo && isTema(p.theme) && aplicarTema(p.theme))
      .catch(() => undefined); // sem rede: fica o modo em cache
    return () => {
      vivo = false;
    };
  }, [user]);

  useEffect(() => {
    if (!open) return;
    const fora = (e: PointerEvent) => box.current && !box.current.contains(e.target as Node) && setOpen(false);
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("pointerdown", fora);
    document.addEventListener("keydown", esc);
    return () => {
      document.removeEventListener("pointerdown", fora);
      document.removeEventListener("keydown", esc);
    };
  }, [open]);

  function escolher(t: Tema) {
    const antes = tema;
    aplicarTema(t);
    setErro(undefined);
    api.setPreferences(t).catch(() => {
      aplicarTema(antes);
      setErro("Não foi possível salvar. Tente de novo.");
    });
  }

  return (
    <div className="aparencia" ref={box}>
      <button className="aparencia-btn" aria-haspopup="true" aria-expanded={open} onClick={() => setOpen((o) => !o)}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 3a9 9 0 0 0 0 18z" fill="currentColor" />
        </svg>
        Aparência
      </button>
      {open && (
        <div className="aparencia-menu" role="radiogroup" aria-label="Aparência">
          <strong>Aparência</strong>
          {TEMAS.map((t) => (
            <button
              key={t.id}
              role="radio"
              aria-checked={tema === t.id}
              className={`aparencia-opt ${tema === t.id ? "on" : ""}`}
              onClick={() => escolher(t.id)}
            >
              <span className="aparencia-mini" aria-hidden="true">
                <span style={{ background: MINI[t.id][0] }} />
                <span style={{ background: MINI[t.id][1] }} />
              </span>
              <span>
                <b>{t.nome}</b>
                <small>{t.desc}</small>
              </span>
            </button>
          ))}
          {erro && <span className="aparencia-erro">{erro}</span>}
          <small className="muted">Fica salvo no seu usuário. As aplicações dos laboratórios não mudam.</small>
        </div>
      )}
    </div>
  );
}
