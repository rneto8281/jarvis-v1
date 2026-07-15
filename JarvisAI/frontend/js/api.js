/**
 * api.js
 * Chamadas REST que permanecem fora do WebSocket: login, ações de
 * controle (ligar/desligar voz e palmas) e carregamento inicial de
 * tarefas. Toda comunicação de streaming (chat, status, transcrição)
 * acontece via ws.js.
 */

import { obterTokenSalvo, limparToken } from "./auth.js";

const BASE_URL = "/api";

async function requisitar(caminho, opcoes = {}) {
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${obterTokenSalvo()}`,
    },
    ...opcoes,
  });

  if (resposta.status === 401) {
    // Token expirado (ex.: backend reiniciado) - força novo login.
    limparToken();
    location.reload();
    throw new Error("Sessão expirada.");
  }

  if (!resposta.ok) {
    throw new Error(`Falha na requisição: ${resposta.status}`);
  }

  return resposta.json();
}

export const JarvisApi = {
  listarTarefas() {
    return requisitar("/system/tarefas");
  },
  iniciarVoz() {
    return requisitar("/voice/start", { method: "POST" });
  },
  pararVoz() {
    return requisitar("/voice/stop", { method: "POST" });
  },
  iniciarPalmas() {
    return requisitar("/voice/palmas/start", { method: "POST" });
  },
  pararPalmas() {
    return requisitar("/voice/palmas/stop", { method: "POST" });
  },
  statusVoz() {
    return requisitar("/voice/status");
  },
};
