/**
 * systemMonitor.js
 * Renderiza os gauges de CPU/RAM/disco e o painel de rede, atualizados
 * em tempo real via WebSocket (evento "status_sistema") — sem nenhum
 * polling do frontend.
 */

import { on } from "./ws.js";

const RAIO = 24;
const CIRCUNFERENCIA = 2 * Math.PI * RAIO;

const METRICAS = [
  { chave: "cpu_percent", label: "CPU", detalheFn: (s) => `${s.cpu_percent.toFixed(0)}% em uso` },
  {
    chave: "ram_percent",
    label: "RAM",
    detalheFn: (s) => `${s.ram_usada_gb}GB / ${s.ram_total_gb}GB`,
  },
  {
    chave: "disco_percent",
    label: "Disco",
    detalheFn: (s) => `${s.disco_usado_gb}GB / ${s.disco_total_gb}GB`,
  },
];

function criarGaugeHTML(id, label) {
  return `
    <div class="gauge" id="gauge-${id}">
      <div class="gauge__ring">
        <svg width="54" height="54" viewBox="0 0 60 60">
          <circle class="track" cx="30" cy="30" r="${RAIO}"></circle>
          <circle class="value" cx="30" cy="30" r="${RAIO}"
            stroke-dasharray="${CIRCUNFERENCIA}"
            stroke-dashoffset="${CIRCUNFERENCIA}"></circle>
        </svg>
        <div class="pct">0%</div>
      </div>
      <div class="gauge__meta">
        <div class="label">${label}</div>
        <div class="detail">—</div>
      </div>
    </div>
  `;
}

function atualizarGauge(id, percentual, detalheTexto) {
  const gauge = document.getElementById(`gauge-${id}`);
  if (!gauge) return;

  const offset = CIRCUNFERENCIA - (percentual / 100) * CIRCUNFERENCIA;
  gauge.querySelector(".value").style.strokeDashoffset = offset;
  gauge.querySelector(".pct").textContent = `${Math.round(percentual)}%`;
  gauge.querySelector(".detail").textContent = detalheTexto;
}

export function iniciarMonitorSistema() {
  const container = document.getElementById("vitals-list");
  container.innerHTML = METRICAS.map((m) => criarGaugeHTML(m.chave, m.label)).join("");

  const netDetail = document.getElementById("net-detail");

  on("status_sistema", (status) => {
    METRICAS.forEach((m) => {
      atualizarGauge(m.chave, status[m.chave], m.detalheFn(status));
    });

    netDetail.innerHTML = `
      <div class="feed-item">Enviado: <strong>${status.rede_enviado_mb} MB</strong></div>
      <div class="feed-item">Recebido: <strong>${status.rede_recebido_mb} MB</strong></div>
      <div class="feed-item">${status.sistema_operacional}</div>
      ${
        status.bateria_percent !== null
          ? `<div class="feed-item">Bateria: ${status.bateria_percent}% ${status.bateria_carregando ? "(carregando)" : ""}</div>`
          : ""
      }
    `;
  });
}
