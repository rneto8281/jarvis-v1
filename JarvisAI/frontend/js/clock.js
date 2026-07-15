/**
 * clock.js
 * Atualiza o relógio e a data exibidos na barra superior.
 */

const MESES = [
  "janeiro", "fevereiro", "março", "abril", "maio", "junho",
  "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
];

export function iniciarRelogio() {
  const elTime = document.getElementById("clock-time");
  const elDate = document.getElementById("clock-date");

  function atualizar() {
    const agora = new Date();
    const hh = String(agora.getHours()).padStart(2, "0");
    const mm = String(agora.getMinutes()).padStart(2, "0");
    const ss = String(agora.getSeconds()).padStart(2, "0");

    elTime.textContent = `${hh}:${mm}:${ss}`;
    elDate.textContent = `${agora.getDate()} de ${MESES[agora.getMonth()]} de ${agora.getFullYear()}`;
  }

  atualizar();
  setInterval(atualizar, 1000);
}
