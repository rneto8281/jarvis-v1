/**
 * chat.js
 * Console de conversa unificado: renderiza toda interação (texto ou
 * voz) a partir dos eventos "mensagem_usuario" e "resposta" recebidos
 * via WebSocket — nunca a partir da resposta direta de uma requisição
 * local, garantindo uma única fonte de verdade para o histórico visual.
 */

import { on, enviar } from "./ws.js";
import { Sons } from "./sounds.js";

function criarBalao(texto, autor, meta) {
  const balao = document.createElement("div");
  balao.className = `msg msg--${autor}`;
  balao.textContent = texto;

  if (meta) {
    const metaEl = document.createElement("span");
    metaEl.className = "msg__meta";
    metaEl.textContent = meta;
    balao.appendChild(metaEl);
  }

  return balao;
}

function registrarAtividade(texto) {
  const log = document.getElementById("activity-log");
  const vazio = log.querySelector(".empty-state");
  if (vazio) vazio.remove();

  const hora = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  const item = document.createElement("div");
  item.className = "feed-item";
  item.innerHTML = `<span class="feed-time">${hora}</span>${texto}`;
  log.prepend(item);
}

export function iniciarChat(controladorNucleo, aoReceberResposta) {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const log = document.getElementById("chat-log");

  form.addEventListener("submit", (evento) => {
    evento.preventDefault();

    const texto = input.value.trim();
    if (!texto) return;

    controladorNucleo.pensando();
    enviar({ tipo: "chat", mensagem: texto });
    input.value = "";
  });

  // Toda mensagem do usuário (via texto OU voz) chega por aqui.
  on("mensagem_usuario", (dados) => {
    log.appendChild(criarBalao(dados.texto, "user"));
    log.scrollTop = log.scrollHeight;
  });

  // Toda resposta do Jarvis (via texto OU voz) chega por aqui.
  on("resposta", (dados) => {
    controladorNucleo.respondendo();
    log.appendChild(criarBalao(dados.texto, "jarvis", `intent: ${dados.intent}`));
    log.scrollTop = log.scrollHeight;

    registrarAtividade(`Intenção reconhecida: <strong>${dados.intent}</strong>`);

    if (dados.intent === "desconhecida" || dados.intent === "entrada_invalida") {
      Sons.erro();
    } else {
      Sons.confirmacao();
    }

    setTimeout(() => controladorNucleo.standby(), 900);

    if (aoReceberResposta) aoReceberResposta();
  });

  // Efeito visual especial para gatilhos como "papai chegou" — disparado
  // pelo backend independentemente da origem (texto, voz ou palmas).
  on("efeito_visual", () => {
    controladorNucleo.efeitoEspecial();
    Sons.confirmacao();
  });
}
