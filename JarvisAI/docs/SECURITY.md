# Segurança do JarvisAI

## Modelo de ameaça

O JarvisAI é um assistente **pessoal**, pensado para rodar em
`127.0.0.1` na sua própria máquina. O objetivo da autenticação **não**
é proteger contra um atacante remoto sofisticado — é impedir que
qualquer outra aba do navegador, site ou processo na mesma máquina
consiga controlar o Jarvis (abrir sites, tocar áudio, ligar o
microfone) sem uma senha explícita.

## Como funciona

- Na primeira execução, uma senha padrão (`"jarvis"`, ou o valor da
  variável de ambiente `JARVIS_PASSWORD`) é definida e seu **hash**
  (PBKDF2-HMAC-SHA256, 200 mil iterações, com salt aleatório) é salvo
  em `backend/database/.credentials.json`. A senha em texto puro nunca
  é armazenada.
- O frontend pede a senha uma vez (`POST /api/auth/login`) e recebe um
  **token de sessão** aleatório, guardado no `localStorage` do
  navegador.
- Todas as rotas HTTP (`/api/chat`, `/api/system/*`, `/api/voice/*`) e
  a conexão WebSocket (`/ws`) exigem esse token.
- Tokens vivem em memória e são invalidados quando o servidor reinicia
  — nesse caso, o frontend detecta automaticamente e pede login de novo.

## Trocar a senha

```powershell
# 1. Defina a nova senha antes de iniciar o servidor:
$env:JARVIS_PASSWORD = "sua-nova-senha-aqui"

# 2. Apague o arquivo de credenciais antigo:
del backend\database\.credentials.json

# 3. Inicie o servidor normalmente - a nova senha será usada:
python -m backend
```

## Sanitização de entrada

Toda mensagem (texto ou transcrição de voz) passa por
`backend/security/sanitizer.py` antes de chegar ao motor de intents:
remove tags HTML/script, caracteres de controle, e limita o tamanho
máximo (500 caracteres) para reduzir a superfície de ataque.

## Execução de comandos

Nenhum plugin executa comandos de shell arbitrários ou `eval` sobre a
entrada do usuário. As ações disponíveis (abrir navegador, tocar uma
música no YouTube, consultar a Wikipedia) são todas pré-definidas no
código dos plugins — o texto do usuário nunca vira código executado.
