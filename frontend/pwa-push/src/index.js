import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

// Adicionar tratamento de erro global
window.addEventListener('error', (event) => {
  console.error('Erro global:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Promise rejeitada:', event.reason);
});

// Verificar se o elemento existe
const appElement = document.getElementById("app");
if (!appElement) {
  console.error("Elemento #app não encontrado!");
  document.body.innerHTML = '<div style="padding: 20px; color: red;">Erro: Elemento #app não encontrado!</div>';
} else {
  try {
    console.log("Iniciando renderização do React...");
    const root = createRoot(appElement);
    root.render(<App />);
    console.log("React renderizado com sucesso!");
  } catch (error) {
    console.error("Erro ao renderizar React:", error);
    appElement.innerHTML = `<div style="padding: 20px; color: red;">Erro ao renderizar: ${error.message}</div>`;
  }
} 