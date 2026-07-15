"""Rotas relacionadas ao monitoramento de sistema e plugins."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.schemas import PluginInfo, StatusSistemaSaida, TarefaSaida
from backend.bootstrap import obter_jarvis_engine, obter_system_monitor
from backend.core.jarvis_engine import JarvisEngine
from backend.services.system_monitor import SystemMonitor

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status", response_model=StatusSistemaSaida)
def status_sistema(monitor: SystemMonitor = Depends(obter_system_monitor)) -> StatusSistemaSaida:
    """Retorna uma coleta atual de métricas de hardware."""

    snap = monitor.coletar()
    return StatusSistemaSaida(**snap.__dict__)


@router.get("/plugins", response_model=list[PluginInfo])
def listar_plugins(engine: JarvisEngine = Depends(obter_jarvis_engine)) -> list[PluginInfo]:
    """Lista os plugins atualmente carregados no sistema."""

    return [PluginInfo(**p) for p in engine.plugin_manager.listar_plugins()]


@router.get("/tarefas", response_model=list[TarefaSaida])
def listar_tarefas(engine: JarvisEngine = Depends(obter_jarvis_engine)) -> list[TarefaSaida]:
    """Lista as tarefas/lembretes pendentes do usuário."""

    return [TarefaSaida(**t) for t in engine.memory.listar_tarefas()]
