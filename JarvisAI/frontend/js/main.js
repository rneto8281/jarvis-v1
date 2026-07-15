/**
 * main.js
 * Ponto de entrada do frontend: exige autenticação, conecta o
 * WebSocket único e inicializa todos os módulos da UI.
 */

import { iniciarRelogio } from "./clock.js";
import { iniciarMonitorSistema } from "./systemMonitor.js";
import { criarControladorDoNucleo } from "./coreOrb.js";
import { iniciarChat } from "./chat.js";
import { iniciarControleDeVoz } from "./voice.js";
import { carregarTarefas } from "./tasks.js";
import { exigirAutenticacao, limparToken } from "./auth.js";
import { conectar, on } from "./ws.js";

document.addEventListener("DOMContentLoaded", async () => {
  const token = await exigirAutenticacao();

  conectar(token);

  on("_desconectado", () => {
    document.getElementById("status-label").textContent = "reconectando…";
  });
  on("_conectado", () => {
    document.getElementById("status-label").textContent = "online";
  });
  on("_token_invalido", () => {
    // Sessão expirada (ex.: backend reiniciado): força novo login.
    limparToken();
    location.reload();
  });

  iniciarRelogio();
  iniciarMonitorSistema();

  const nucleo = criarControladorDoNucleo();
  iniciarChat(nucleo, carregarTarefas);
  iniciarControleDeVoz(nucleo);

  carregarTarefas();
});
