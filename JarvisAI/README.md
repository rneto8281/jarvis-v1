# JarvisAI

Uma assistente de IA modular inspirada no J.A.R.V.I.S., com backend em
Python (FastAPI + WebSocket) e um painel de controle web em HTML/CSS/JS
puro, no estilo HUD futurista, com voz, detecção de palmas e
comunicação em tempo real.

## Funcionalidades

- **Conversa unificada em tempo real** (WebSocket): texto e voz aparecem
  no mesmo console, sem polling
- **Reconhecimento e síntese de voz**: fale com o Jarvis e ouça a
  resposta de volta
- **Detecção de duas palmas**: aciona a mesma rotina do comando
  "papai chegou" (música do Tony Stark + modo de escuta)
- **Autenticação local** por senha, protegendo a API e o WebSocket
- **Motor de intents** com sinônimos expandidos e stemming leve em
  português (reconhece variações verbais sem exigir NLTK)
- **Feedback sonoro** sintetizado (início/fim de escuta, reconhecimento,
  erro, confirmação) via Web Audio API
- **Painel web em tempo real**: relógio, CPU/RAM/disco/rede, tarefas,
  log de atividade — tudo via push do WebSocket
- **Sistema de plugins independentes**, testes automatizados e CI

## Como executar (Windows)

```powershell
setup.bat     REM primeira vez: cria venv e instala tudo
run.bat       REM inicia o servidor
```

Ou manualmente, em qualquer sistema:

```bash
python -m pip install -r requirements.txt
python -m backend
```

Acesse `http://127.0.0.1:8000`. Na primeira execução, a senha padrão é
`jarvis` (troque seguindo `docs/SECURITY.md`).

## Rodar os testes

```bash
pip install pytest
pytest tests/ -v
```

O CI (`.github/workflows/tests.yml`) roda os mesmos testes
automaticamente a cada push/PR no GitHub.

## Estrutura do projeto

```
JarvisAI/
├── backend/
│   ├── core/          # Motor de IA: intents, contexto, orquestração, eventos
│   ├── memory/         # Memória de longo prazo (perfil, histórico, tarefas)
│   ├── plugins/         # Comandos, cada um em um módulo independente
│   ├── services/         # Monitoramento de sistema
│   ├── voice/              # Reconhecimento de voz, síntese, detecção de palmas
│   ├── security/             # Autenticação local e sanitização de entrada
│   ├── database/               # Camada de acesso a dados (SQLite)
│   ├── api/                      # FastAPI: rotas REST, WebSocket e DTOs
│   ├── config/                     # Configurações centralizadas
│   ├── utils/                        # Logger, stemmer e utilitários de texto
│   └── bootstrap.py                    # Composição de dependências
├── frontend/
│   ├── css/            # Tokens, layout, componentes, animações
│   └── js/               # Módulos ES6 (ws, auth, chat, voz, sons, gauges)
├── java-services/    # Serviços auxiliares desacoplados (exemplo incluso)
├── tests/               # Testes unitários (pytest)
├── .github/workflows/     # CI
├── setup.bat / install.bat / run.bat   # Scripts de configuração (Windows)
└── docs/
    ├── ARCHITECTURE.md    # Detalhamento da arquitetura e padrões usados
    └── SECURITY.md            # Modelo de ameaça e autenticação
```

## Reconhecimento de voz e detecção de palmas

O botão 🎙 liga/desliga a escuta contínua; o botão 👏 liga/desliga a
detecção de duas palmas. Ambos reaproveitam o mesmo motor de intents
usado no chat de texto.

Dizer (ou digitar, ou bater duas palmas) **"acorda que o papai
chegou"** abre o YouTube tocando "Back In Black Iron Man", ativa
efeitos visuais no núcleo central e entra em modo de conversa contínua
(sem precisar repetir nenhuma palavra de ativação a cada frase).

### Instalação das dependências de voz (Windows)

`PyAudio` costuma falhar ao instalar via `pip` puro no Windows:

```powershell
python -m pip install pipwin
python -m pipwin install pyaudio
python -m pip install SpeechRecognition pyttsx3
```

Sem essas dependências, os botões de microfone/palmas ficam visíveis
mas desabilitados — o resto do sistema funciona normalmente por texto.

## Como criar um novo plugin

1. Crie `backend/plugins/meu_plugin.py` herdando de `BasePlugin`.
2. Implemente `intents_suportadas()` (frases de exemplo + palavras-chave)
   e `executar()` (a lógica do comando).
3. Registre a instância em `backend/bootstrap.py`.

Veja `docs/ARCHITECTURE.md` para o detalhamento completo dos padrões
de projeto e do fluxo de eventos em tempo real via WebSocket.

## Limitações conhecidas

- **Voz do JARVIS dos filmes**: não é possível reproduzir a voz
  original (direitos do estúdio/ator). O sistema usa a melhor voz
  offline disponível no seu sistema operacional (`pyttsx3`), com
  preferência por vozes graves/em português. A arquitetura
  (`VoiceSynthesizer`) foi pensada para permitir plugar um serviço de
  TTS premium (ElevenLabs, Azure) no futuro, se desejado.
- **Latência**: o reconhecimento (`SpeechRecognition`, via Google Web
  Speech API) e a síntese dependem de internet e do hardware local;
  não há garantia de latência abaixo de 500ms — o sistema foi
  otimizado para não adicionar nenhum atraso desnecessário além disso
  (comunicação via WebSocket em vez de polling, sem esperas artificiais).
- **GPU**: métricas limitadas ao que `psutil` expõe de forma
  multiplataforma.
- **Reconhecimento de voz/palmas** funciona com o microfone do
  computador que roda o backend — não captam áudio remotamente do
  navegador de outro dispositivo.
