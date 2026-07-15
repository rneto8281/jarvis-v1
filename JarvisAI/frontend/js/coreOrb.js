/**
 * coreOrb.js
 * Controla o estado visual do núcleo central do HUD, sincronizado com
 * as fases reais de escuta/processamento/fala reportadas pelo backend
 * via WebSocket (evento "voz_fase"), além do fluxo de chat por texto.
 */

const ESTADOS = ["is-listening", "is-thinking", "is-responding"];

export function criarControladorDoNucleo() {
  const orb = document.getElementById("core-orb");
  const wrap = document.querySelector(".core-orb-wrap");
  const label = document.getElementById("core-status-text");

  function definirEstado(estado, texto) {
    ESTADOS.forEach((c) => orb.classList.remove(c));
    if (estado) orb.classList.add(estado);
    label.textContent = texto;
  }

  function dispararEfeitoEspecial() {
    wrap.classList.remove("is-special-effect");
    // Força reflow para permitir reiniciar a animação em cliques seguidos.
    void wrap.offsetWidth;
    wrap.classList.add("is-special-effect");
    setTimeout(() => wrap.classList.remove("is-special-effect"), 1500);
  }

  return {
    standby: () => definirEstado(null, "standby"),
    escutando: () => definirEstado("is-listening", "escutando"),
    pensando: () => definirEstado("is-thinking", "processando"),
    respondendo: () => definirEstado("is-responding", "respondendo"),
    efeitoEspecial: dispararEfeitoEspecial,
  };
}
