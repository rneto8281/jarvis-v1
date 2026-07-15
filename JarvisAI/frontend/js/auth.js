/**
 * auth.js
 * Gerencia o login local (senha) e o token de sessão armazenado no
 * navegador. O token é reenviado em toda requisição REST e na conexão
 * WebSocket, protegendo a API contra uso não autorizado por outras
 * abas/sites na mesma máquina.
 */

const CHAVE_TOKEN = "jarvis_session_token";

export function obterTokenSalvo() {
  return localStorage.getItem(CHAVE_TOKEN);
}

function salvarToken(token) {
  localStorage.setItem(CHAVE_TOKEN, token);
}

export function limparToken() {
  localStorage.removeItem(CHAVE_TOKEN);
}

async function autenticar(senha) {
  const resposta = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha }),
  });

  if (!resposta.ok) {
    throw new Error("Senha incorreta.");
  }

  const dados = await resposta.json();
  salvarToken(dados.token);
  return dados.token;
}

/**
 * Garante que existe um token de sessão válido antes de liberar o
 * restante da aplicação. Se não houver token salvo, exibe a tela de
 * login e só resolve a Promise após autenticação bem-sucedida.
 */
export function exigirAutenticacao() {
  return new Promise((resolve) => {
    const tokenExistente = obterTokenSalvo();

    if (tokenExistente) {
      resolve(tokenExistente);
      return;
    }

    const overlay = document.getElementById("login-overlay");
    const form = document.getElementById("login-form");
    const input = document.getElementById("login-senha");
    const erro = document.getElementById("login-erro");

    overlay.classList.add("is-visible");
    input.focus();

    form.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      erro.textContent = "";

      try {
        const token = await autenticar(input.value);
        overlay.classList.remove("is-visible");
        resolve(token);
      } catch (e) {
        erro.textContent = "Senha incorreta. Tente novamente.";
        input.value = "";
        input.focus();
      }
    });
  });
}
