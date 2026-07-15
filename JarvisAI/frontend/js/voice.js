/**
 * voice.js
 * Controla os botões de microfone (escuta contínua) e palmas. O
 * estado visual é sincronizado via WebSocket ("voz_estado" e
 * "voz_fase"), nunca por polling — a ação de ligar/desligar continua
 * sendo uma chamada REST simples (ação pontual, não um stream).
 */

import { JarvisApi } from "./api.js";
import { on } from "./ws.js";
import { Sons } from "./sounds.js";

export function iniciarControleDeVoz(controladorNucleo) {
  const botaoMic = document.getElementById("mic-toggle");
  const botaoPalmas = document.getElementById("clap-toggle");
  let escutando = false;
  let palmasAtivas = false;

  async function verificarDisponibilidade() {
    try {
      const status = await JarvisApi.statusVoz();

      if (!status.disponivel) {
        botaoMic.title = "Reconhecimento de voz não instalado no backend.";
        botaoMic.disabled = true;
      }
      if (!status.palmas_disponivel) {
        botaoPalmas.title = "Detecção de palmas não instalada no backend (requer PyAudio).";
        botaoPalmas.disabled = true;
      }

      escutando = status.ativo;
      palmasAtivas = status.palmas_ativo;
      botaoMic.classList.toggle("is-active", escutando);
      botaoPalmas.classList.toggle("is-active", palmasAtivas);
    } catch (erro) {
      console.error("Falha ao consultar status de voz:", erro);
    }
  }

  botaoMic.addEventListener("click", async () => {
    try {
      if (escutando) {
        await JarvisApi.pararVoz();
      } else {
        const status = await JarvisApi.iniciarVoz();
        if (!status.disponivel) {
          alert(
            "O reconhecimento de voz não está instalado neste backend.\n" +
            "Veja o README para instalar SpeechRecognition, PyAudio e pyttsx3."
          );
        }
      }
    } catch (erro) {
      console.error("Falha ao alternar escuta por voz:", erro);
    }
  });

  botaoPalmas.addEventListener("click", async () => {
    try {
      if (palmasAtivas) {
        await JarvisApi.pararPalmas();
      } else {
        const status = await JarvisApi.iniciarPalmas();
        if (!status.palmas_disponivel) {
          alert("A detecção de palmas requer PyAudio instalado no backend.");
        }
      }
    } catch (erro) {
      console.error("Falha ao alternar detecção de palmas:", erro);
    }
  });

  // Estado ligado/desligado da escuta contínua.
  on("voz_estado", (dados) => {
    escutando = dados.ativo;
    botaoMic.classList.toggle("is-active", escutando);
  });

  // Fases granulares (escutando/processando/falando), usadas para
  // sincronizar o núcleo central e os efeitos sonoros com o que está
  // realmente acontecendo na pipeline de voz.
  on("voz_fase", (dados) => {
    switch (dados.fase) {
      case "escutando":
        controladorNucleo.escutando();
        Sons.inicioEscuta();
        break;
      case "processando":
        controladorNucleo.pensando();
        Sons.reconhecido();
        break;
      case "falando":
        controladorNucleo.respondendo();
        break;
      case "ociosa":
        controladorNucleo.standby();
        break;
    }
  });

  verificarDisponibilidade();
}
