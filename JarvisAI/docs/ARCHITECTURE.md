# Arquitetura do JarvisAI

## Visão geral

O JarvisAI segue uma **Clean Architecture** simplificada, organizada em
camadas com responsabilidades únicas e comunicação por injeção de
dependência. O ponto de composição único é `backend/bootstrap.py`.

```
Interface (frontend/)
        │  WebSocket (tempo real) + REST (ações pontuais)
        ▼
API (backend/api/)              ← DTOs (Pydantic), rotas HTTP/WS, autenticação
        │
        ▼
Orquestração (backend/core/jarvis_engine.py)   ← Facade
        │
        ├── IntentEngine (core/intent_engine.py)     — NLU leve + stemming
        ├── ContextManager (core/context_manager.py) — memória de curto prazo
        ├── PluginManager (core/plugin_manager.py)   — despacho de comandos
        └── MemoryManager (memory/memory_manager.py) — memória de longo prazo
                    │
                    ▼
            Database (database/db.py)  — SQLite (Repository)

Fontes de entrada paralelas, todas convergindo no mesmo JarvisEngine:
    Chat (texto, via WS) ──┐
    Voz (voice_service.py) ├──► JarvisEngine.processar_mensagem()
    Palmas (clap_detector) ┘──► JarvisEngine.disparar_intent()  (bypassa o NLU)
```

## Comunicação em tempo real (WebSocket)

Toda comunicação entre frontend e backend acontece por um único canal
WebSocket (`/ws`), eliminando o polling da versão anterior:

1. O `EventBus` (síncrono, usado por `JarvisEngine`, `VoiceService` e
   `ClapDetector`) publica eventos como `mensagem_recebida`,
   `resposta_gerada`, `voz_transcrita` e `voz_fase`.
2. `backend/api/routes/ws.py` assina esses eventos na importação do
   módulo e os retransmite para todos os clientes conectados via
   `ConnectionManager` (`backend/api/ws_manager.py`).
3. Como `VoiceService` e `ClapDetector` rodam em *threads* separadas do
   loop de eventos do FastAPI, o broadcast a partir delas usa
   `asyncio.run_coroutine_threadsafe` para agendar o envio de forma
   segura no loop principal (capturado no handshake do WebSocket).
4. Métricas de sistema são transmitidas por uma *task* de fundo
   (`_loop_transmissao_status` em `api/main.py`), a cada 2 segundos,
   sem que o frontend precise pedir nada.

Isso garante um **chat unificado de verdade**: uma mensagem enviada por
voz e uma mensagem digitada passam exatamente pelo mesmo caminho
(`mensagem_recebida` → `resposta_gerada`) e chegam ao mesmo componente
de renderização no frontend (`chat.js`).

## Segurança

- `backend/security/auth.py`: senha local com hash PBKDF2-HMAC-SHA256
  (nunca em texto puro) e tokens de sessão em memória.
- `backend/api/security_deps.py`: dependência `exigir_autenticacao`,
  aplicada a todos os routers de domínio (`chat`, `system`, `voice`) em
  `api/main.py`. O WebSocket valida o token manualmente (query param),
  já que `Depends` de header não se aplica ao handshake.
- `backend/security/sanitizer.py`: toda entrada de texto (chat ou
  transcrição de voz) é sanitizada dentro de
  `JarvisEngine.processar_mensagem` antes de chegar ao motor de intents.

Veja `docs/SECURITY.md` para o modelo de ameaça completo.

## Fluxo de uma mensagem

1. O frontend envia `POST /api/chat` com o texto do usuário.
2. `JarvisEngine.processar_mensagem` publica o evento `mensagem_recebida`.
3. `IntentEngine` classifica a intenção (palavra-chave + similaridade fuzzy).
4. Se a intenção for conhecida, `PluginManager` despacha para o plugin
   responsável, passando um `PluginContext` com a entidade extraída e o
   último tópico de conversa (para perguntas de acompanhamento).
5. O turno é registrado no `ContextManager` (memória de curto prazo, em
   RAM) e no `MemoryManager` (memória de longo prazo, em SQLite).
6. O evento `resposta_gerada` é publicado (consumido futuramente por
   síntese de voz ou animações adicionais da UI).

## Padrões de projeto aplicados

| Padrão | Onde | Por quê |
|---|---|---|
| Facade | `JarvisEngine` | Interface única e simples para a API |
| Strategy | `IntentEngine`, plugins | Cada plugin implementa sua própria lógica sob um contrato comum |
| Plugin/Registry | `PluginManager` | Novos comandos sem alterar o núcleo |
| Repository | `database/db.py`, `MemoryManager` | Isola SQL do restante do sistema |
| Observer | `EventBus` | Desacopla produtores e consumidores de eventos |
| Dependency Injection | `bootstrap.py` | Único ponto de composição de dependências |
| Singleton (simplificado) | `settings`, `event_bus`, `lru_cache` no bootstrap | Instâncias únicas e compartilhadas |

## Extensibilidade

- **Novo plugin**: crie uma classe em `backend/plugins/` herdando de
  `BasePlugin`, implemente `intents_suportadas()` e `executar()`, e
  registre-a em `bootstrap.py`.
- **Nova intenção em um plugin existente**: adicione uma nova
  `IntentDefinition` ao método `intents_suportadas()`.
- **Trocar SQLite por PostgreSQL**: a camada `database/db.py` isola
  toda a lógica de conexão; `config/settings.py` já expõe
  `postgres_dsn` para quando a migração for necessária.
- **Voz**: o `JarvisEngine.processar_mensagem` é agnóstico à origem do
  texto — um módulo de reconhecimento de voz futuro só precisa chamar
  esse mesmo método com o texto transcrito.
