"""
Ponto de entrada da API local do JarvisAI.

Sobe um servidor FastAPI que expõe o motor do Jarvis (chat, sistema,
tarefas, plugins, voz) para a interface web via HTTP e WebSocket, e
também serve os arquivos estáticos do frontend.

Todas as rotas de domínio (`chat`, `system`, `voice`) exigem um token
de sessão válido, obtido via `POST /api/auth/login`. A rota de
WebSocket (`/ws`) também exige o token, como query param.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import auth, chat, system, voice, ws
from backend.api.security_deps import exigir_autenticacao
from backend.api.ws_manager import connection_manager
from backend.bootstrap import obter_system_monitor
from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

_INTERVALO_STATUS_SEGUNDOS = 2.0


async def _loop_transmissao_status() -> None:
    """Task de fundo que empurra métricas de sistema via WebSocket em
    intervalos regulares, substituindo o polling que o frontend fazia
    na versão anterior."""

    monitor = obter_system_monitor()

    while True:
        try:
            snap = monitor.coletar()
            await connection_manager.transmitir({"tipo": "status_sistema", **snap.__dict__})
        except Exception:  # noqa: BLE001 - não pode derrubar a task de fundo
            logger.exception("Falha ao transmitir status do sistema.")

        await asyncio.sleep(_INTERVALO_STATUS_SEGUNDOS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação: inicia a task de status
    do sistema na subida e a cancela no encerramento."""

    task = asyncio.create_task(_loop_transmissao_status())
    logger.info("JarvisAI iniciado.")
    yield
    task.cancel()
    logger.info("JarvisAI encerrado.")


app = FastAPI(
    title="JarvisAI",
    description="API local da assistente de IA JarvisAI.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota pública (sem autenticação): login.
app.include_router(auth.router)

# Rotas protegidas: exigem token de sessão válido.
app.include_router(chat.router, dependencies=[Depends(exigir_autenticacao)])
app.include_router(system.router, dependencies=[Depends(exigir_autenticacao)])
app.include_router(voice.router, dependencies=[Depends(exigir_autenticacao)])

# WebSocket: autenticação verificada internamente (query param), pois
# `Depends` de header não se aplica bem ao handshake de WebSocket.
app.include_router(ws.router)

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
