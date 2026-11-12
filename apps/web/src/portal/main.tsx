import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

// Tickets e cookies do gateway são do host 127.0.0.1; "localhost" seria outro site.
if (location.hostname === "localhost") {
  location.replace(location.href.replace("//localhost", "//127.0.0.1"));
} else {
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
