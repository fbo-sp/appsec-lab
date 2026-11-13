import { useCallback, useEffect, useRef, useState } from "react";
import type { KeyboardEvent, PointerEvent, RefObject } from "react";

const KEY = "cecyber.stepsWidth";
export const DEFAULT_STEPS_WIDTH = 320;
const MIN = 260;
const STEP = 24;

function maxFor(container: HTMLElement | null): number {
  // O painel de etapas nunca passa de 60% da área, para as abas continuarem usáveis.
  const total = container?.clientWidth ?? window.innerWidth;
  return Math.max(MIN, Math.round(total * 0.6));
}

function readStored(): number {
  try {
    const v = Number(window.localStorage.getItem(KEY));
    return Number.isFinite(v) && v >= MIN ? v : DEFAULT_STEPS_WIDTH;
  } catch {
    return DEFAULT_STEPS_WIDTH;
  }
}

/** Largura do painel de etapas, ajustável pelo aluno e lembrada neste navegador. */
export function useStepsWidth(container: RefObject<HTMLElement | null>) {
  const [width, setWidth] = useState(readStored);
  const clamp = useCallback(
    (w: number) => Math.min(maxFor(container.current), Math.max(MIN, Math.round(w))),
    [container],
  );

  useEffect(() => {
    try {
      window.localStorage.setItem(KEY, String(width));
    } catch {
      /* armazenamento indisponível: vale só nesta página */
    }
  }, [width]);

  // Janela encolheu: mantém o painel dentro do limite.
  useEffect(() => {
    const onResize = () => setWidth((w) => clamp(w));
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [clamp]);

  return { width, setWidth: (w: number) => setWidth(clamp(w)), min: MIN, max: () => maxFor(container.current) };
}

export function Splitter({
  width,
  min,
  max,
  onChange,
  onDragging,
}: {
  width: number;
  min: number;
  max: () => number;
  onChange: (w: number) => void;
  onDragging: (on: boolean) => void;
}) {
  const start = useRef<{ x: number; w: number } | undefined>(undefined);

  function down(e: PointerEvent<HTMLDivElement>) {
    if (e.button !== 0) return;
    e.preventDefault();
    e.currentTarget.setPointerCapture(e.pointerId);
    start.current = { x: e.clientX, w: width };
    onDragging(true);
  }
  function move(e: PointerEvent<HTMLDivElement>) {
    if (!start.current) return;
    onChange(start.current.w + e.clientX - start.current.x);
  }
  function up(e: PointerEvent<HTMLDivElement>) {
    if (!start.current) return;
    start.current = undefined;
    e.currentTarget.releasePointerCapture(e.pointerId);
    onDragging(false);
  }
  function key(e: KeyboardEvent<HTMLDivElement>) {
    const next =
      e.key === "ArrowLeft" ? width - STEP
      : e.key === "ArrowRight" ? width + STEP
      : e.key === "Home" ? min
      : e.key === "End" ? max()
      : undefined;
    if (next === undefined) return;
    e.preventDefault();
    onChange(next);
  }

  return (
    <div
      className="splitter"
      role="separator"
      aria-orientation="vertical"
      aria-label="Ajustar largura do painel de etapas"
      aria-valuenow={width}
      aria-valuemin={min}
      aria-valuemax={max()}
      tabIndex={0}
      title="Arraste para ajustar. Duplo clique volta ao tamanho padrão."
      onPointerDown={down}
      onPointerMove={move}
      onPointerUp={up}
      onPointerCancel={up}
      onKeyDown={key}
      onDoubleClick={() => onChange(DEFAULT_STEPS_WIDTH)}
    />
  );
}
