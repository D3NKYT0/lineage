import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const appElement = document.getElementById("app");
if (!appElement) {
  document.body.innerHTML = '<div class="pwa-container" role="alert"><p>Erro: aplicação não pôde ser carregada.</p></div>';
} else {
  const root = createRoot(appElement);
  root.render(<App />);
}
