import { useEffect, useRef } from "react";

/** Ícone "i" ao lado da barra de endereço da aba Aplicação: explica para que ela serve e onde fica.
 * Enquanto a explicação está aberta, a barra real recebe destaque (classe aplicada pelo pai via `open`). */
export function AddressHelp({ open, onToggle }: { open: boolean; onToggle: (open: boolean) => void }) {
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onToggle(false);
    const onClick = (e: MouseEvent) => {
      if (box.current && !box.current.contains(e.target as Node)) onToggle(false);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onClick);
    };
  }, [open, onToggle]);

  return (
    <div className="address-help" ref={box}>
      <button
        type="button"
        className="info-btn"
        aria-label="Como usar a barra de endereço"
        aria-expanded={open}
        onClick={() => onToggle(!open)}
      >
        i
      </button>
      {open && (
        <div className="address-help-pop" role="dialog" aria-label="Como usar a barra de endereço">
          <strong>Barra de endereço da aplicação</strong>
          <div className="address-help-mock" aria-hidden="true">
            <span className="mock-field">/comprovantes/10458</span>
            <span className="mock-link">ir</span>
            <span className="mock-link">recarregar</span>
            <span className="mock-link">abrir em nova aba</span>
          </div>
          <p>
            Ela fica aqui em cima, destacada agora, e funciona como a barra de endereço de um navegador, só que
            para a aplicação do laboratório.
          </p>
          <ol>
            <li>
              Apague o que estiver no campo e digite um caminho começando com <code>/</code>, por exemplo{" "}
              <code>/api/comprovantes/10458</code>.
            </li>
            <li>
              Pressione <kbd>Enter</kbd> ou clique em <b>ir</b>. A página abaixo mostra o resultado.
            </li>
          </ol>
          <p>
            Prefere o navegador de sempre? Clique em <b>abrir em nova aba</b> e edite o endereço lá, normalmente.
          </p>
          <button type="button" className="link" onClick={() => onToggle(false)}>
            entendi
          </button>
        </div>
      )}
    </div>
  );
}
