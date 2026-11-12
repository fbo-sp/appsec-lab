import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Workspace } from "./Workspace";
import "@xterm/xterm/css/xterm.css";
import "./workspace.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Workspace />
  </StrictMode>,
);
