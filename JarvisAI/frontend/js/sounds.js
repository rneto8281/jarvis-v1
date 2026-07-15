/**
 * sounds.js
 * Feedback sonoro do HUD, sintetizado via Web Audio API — sem
 * arquivos de áudio externos, apenas tons curtos gerados em tempo
 * real (leve e sem dependências).
 */

let contextoAudio = null;

function obterContexto() {
  if (!contextoAudio) {
    contextoAudio = new (window.AudioContext || window.webkitAudioContext)();
  }
  return contextoAudio;
}

function tocarTom(frequencia, duracaoMs, tipo = "sine", volume = 0.08) {
  const ctx = obterContexto();
  const oscilador = ctx.createOscillator();
  const ganho = ctx.createGain();

  oscilador.type = tipo;
  oscilador.frequency.value = frequencia;
  ganho.gain.value = volume;

  oscilador.connect(ganho);
  ganho.connect(ctx.destination);

  const agora = ctx.currentTime;
  ganho.gain.setValueAtTime(volume, agora);
  ganho.gain.exponentialRampToValueAtTime(0.0001, agora + duracaoMs / 1000);

  oscilador.start(agora);
  oscilador.stop(agora + duracaoMs / 1000);
}

export const Sons = {
  inicioEscuta() {
    tocarTom(880, 90);
    setTimeout(() => tocarTom(1180, 90), 90);
  },
  fimEscuta() {
    tocarTom(1180, 90);
    setTimeout(() => tocarTom(880, 90), 90);
  },
  reconhecido() {
    tocarTom(1400, 60, "triangle");
  },
  erro() {
    tocarTom(220, 220, "sawtooth", 0.06);
  },
  confirmacao() {
    tocarTom(660, 70);
    setTimeout(() => tocarTom(990, 110), 80);
  },
};
