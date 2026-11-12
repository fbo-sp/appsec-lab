import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dois pontos de entrada: o portal (origem da API) e o workspace (origem do gateway).
export default defineConfig({
  base: "/__static/",
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      input: {
        index: "index.html",
        workspace: "workspace.html",
      },
    },
  },
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
