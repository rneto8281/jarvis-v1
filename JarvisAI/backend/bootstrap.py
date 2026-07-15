"""
Bootstrap da aplicação: composição de dependências (Composition Root).

Este é o único lugar do sistema onde as implementações concretas são
instanciadas e conectadas entre si. Toda a aplicação (API, e futuramente
voz/CLI) deve obter suas instâncias através deste módulo, nunca
instanciando os componentes centrais diretamente — isso mantém o
princípio de Injeção de Dependência consistente em todo o projeto.
"""

from __future__ import annotations

from functools import lru_cache

from backend.core.context_manager import ContextManager
from backend.core.intent_engine import IntentEngine
from backend.core.jarvis_engine import JarvisEngine
from backend.core.plugin_manager import PluginManager
from backend.database.db import Database
from backend.memory.memory_manager import MemoryManager
from backend.plugins.conversa_plugin import ConversaPlugin
from backend.plugins.datetime_plugin import DateTimePlugin
from backend.plugins.easter_egg_plugin import EasterEggPlugin
from backend.plugins.musica_plugin import MusicaPlugin
from backend.plugins.navegacao_plugin import NavegacaoPlugin
from backend.plugins.pesquisa_plugin import PesquisaPlugin
from backend.plugins.piada_plugin import PiadaPlugin
from backend.plugins.sistema_plugin import SistemaPlugin
from backend.plugins.tarefas_plugin import TarefasPlugin
from backend.security.auth import AuthService
from backend.voice.clap_detector import ClapDetector
from backend.services.system_monitor import SystemMonitor
from backend.voice.voice_service import VoiceService


@lru_cache(maxsize=1)
def obter_jarvis_engine() -> JarvisEngine:
    """Constrói (uma única vez) e retorna a instância principal do
    motor do JarvisAI, com todos os plugins já registrados.

    Usa ``lru_cache`` para funcionar como um Singleton simples e
    compatível com o sistema de injeção de dependências do FastAPI.
    """

    database = Database()
    memory_manager = MemoryManager(database)
    intent_engine = IntentEngine()
    plugin_manager = PluginManager(intent_engine)
    context_manager = ContextManager()

    plugin_manager.registrar(ConversaPlugin(memory_manager))
    plugin_manager.registrar(EasterEggPlugin())
    plugin_manager.registrar(DateTimePlugin())
    plugin_manager.registrar(NavegacaoPlugin())
    plugin_manager.registrar(PesquisaPlugin())
    plugin_manager.registrar(MusicaPlugin())
    plugin_manager.registrar(PiadaPlugin())
    plugin_manager.registrar(SistemaPlugin(SystemMonitor()))
    plugin_manager.registrar(TarefasPlugin(memory_manager))

    return JarvisEngine(
        intent_engine=intent_engine,
        plugin_manager=plugin_manager,
        context_manager=context_manager,
        memory_manager=memory_manager,
    )


@lru_cache(maxsize=1)
def obter_memory_manager() -> MemoryManager:
    """Retorna a instância compartilhada do gerenciador de memória."""

    return obter_jarvis_engine().memory


@lru_cache(maxsize=1)
def obter_system_monitor() -> SystemMonitor:
    """Retorna a instância compartilhada do monitor de sistema."""

    return SystemMonitor()


@lru_cache(maxsize=1)
def obter_voice_service() -> VoiceService:
    """Retorna a instância compartilhada do serviço de voz, já ligada
    ao mesmo motor central usado pelo chat de texto."""

    return VoiceService(jarvis_engine=obter_jarvis_engine())


@lru_cache(maxsize=1)
def obter_auth_service() -> AuthService:
    """Retorna a instância compartilhada do serviço de autenticação local."""

    return AuthService()


@lru_cache(maxsize=1)
def obter_clap_detector() -> ClapDetector:
    """Retorna a instância compartilhada do detector de palmas, ligada
    ao mesmo motor central usado pelo chat e pela voz."""

    return ClapDetector(jarvis_engine=obter_jarvis_engine())
