/**
 * tasks.js
 * Carrega e renderiza a lista de tarefas pendentes. A lista é
 * recarregada no início e sempre que uma resposta do Jarvis chega
 * (heurística simples: qualquer interação pode ter criado/alterado
 * uma tarefa, e a chamada é barata).
 */

import { JarvisApi } from "./api.js";

export async function carregarTarefas() {
  const container = document.getElementById("task-list");

  try {
    const tarefas = await JarvisApi.listarTarefas();

    if (tarefas.length === 0) {
      container.innerHTML = '<div class="empty-state">Nenhuma tarefa registrada.</div>';
      return;
    }

    container.innerHTML = tarefas
      .map((t) => `<div class="task-item">${t.descricao}</div>`)
      .join("");
  } catch (erro) {
    console.error("Falha ao carregar tarefas:", erro);
  }
}
