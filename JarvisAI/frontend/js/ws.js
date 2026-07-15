/**
 * ws.js
 * Cliente WebSocket único do JarvisAI. Substitui todo o polling
 * anterior: mensagens de chat, transcrições de voz, mudanças de
 * estado e métricas de sistema chegam todas por este canal.
 *
 * Implementa um pub/sub simples (`on`) para que outros módulos se
 * inscrevam em tipos de evento sem acoplamento direto à conexão.
 */

const ouvintes = new Map();
let socket = null;
let filaEnvio = [];

function notificar(tipo, dados) {
  const callbacks = ouvintes.get(tipo) || [];
  callbacks.forEach((cb) => cb(dados));
}

export function on(tipo, callback) {
  if (!ouvintes.has(tipo)) ouvintes.set(tipo, []);
  ouvintes.get(tipo).push(callback);
}

export function enviar(objeto) {
  const payload = JSON.stringify(objeto);

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(payload);
  } else {
    filaEnvio.push(payload);
  }
}

export function conectar(token) {
  const protocolo = location.protocol === "https:" ? "wss:" : "ws:";
  socket = new WebSocket(`${protocolo}//${location.host}/ws?token=${encodeURIComponent(token)}`);

  socket.addEventListener("open", () => {
    notificar("_conectado", {});
    filaEnvio.forEach((payload) => socket.send(payload));
    filaEnvio = [];
  });

  socket.addEventListener("message", (evento) => {
    try {
      const dados = JSON.parse(evento.data);
      notificar(dados.tipo, dados);
    } catch (erro) {
      console.error("Mensagem WebSocket inválida:", erro);
    }
  });

  socket.addEventListener("close", (evento) => {
    notificar("_desconectado", {});

    // Token inválido/expirado (código customizado 4401 do backend):
    // força novo login em vez de tentar reconectar em loop.
    if (evento.code === 4401) {
      notificar("_token_invalido", {});
      return;
    }

    // Reconexão simples com backoff fixo — suficiente para um
    // assistente local rodando na mesma máquina.
    setTimeout(() => conectar(token), 2000);
  });
}
