"""
Gerenciador de plugins do JarvisAI.

Responsável por descobrir, registrar e despachar comandos para os
plugins instalados. Segue o padrão Registry combinado com Strategy:
cada intenção reconhecida é mapeada para o plugin capaz de tratá-la.
"""

from __future__ import annotations

from backend.core.intent_engine import IntentEngine
from backend.plugins.base_plugin import BasePlugin, PluginContext
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PluginManager:
    """Orquestra o ciclo de vida dos plugins: registro e despacho."""

    def __init__(self, intent_engine: IntentEngine) -> None:
        self._intent_engine = intent_engine
        self._plugins: dict[str, BasePlugin] = {}
        self._mapa_intent_para_plugin: dict[str, BasePlugin] = {}

    def registrar(self, plugin: BasePlugin) -> None:
        """Registra um plugin, expondo suas intenções ao motor de NLU.

        Cada intenção declarada pelo plugin é registrada no
        ``IntentEngine`` e mapeada de volta para o próprio plugin, para
        que o despacho seja O(1) após a classificação.
        """

        self._plugins[plugin.nome] = plugin

        for intent_def in plugin.intents_suportadas():
            self._intent_engine.registrar_intent(intent_def)
            self._mapa_intent_para_plugin[intent_def.nome] = plugin

        logger.info("Plugin registrado: %s", plugin.nome)

    def obter_plugin_para_intent(self, intent: str) -> BasePlugin | None:
        """Retorna o plugin responsável por uma intenção, se houver."""

        return self._mapa_intent_para_plugin.get(intent)

    def despachar(self, intent: str, contexto: PluginContext) -> str | None:
        """Executa o plugin responsável pela intenção informada.

        Returns:
            A resposta do plugin, ou ``None`` se nenhum plugin tratar
            essa intenção (o chamador deve tratar como "não entendi").
        """

        plugin = self.obter_plugin_para_intent(intent)
        if plugin is None:
            return None

        try:
            return plugin.executar(contexto)
        except Exception:  # noqa: BLE001 - isolamento de falhas por plugin
            logger.exception("Erro ao executar plugin '%s'", plugin.nome)
            return "Encontrei um problema ao executar essa ação. Já registrei o erro nos logs."

    def listar_plugins(self) -> list[dict[str, str]]:
        """Lista os plugins carregados, para fins de documentação/UI."""

        return [
            {"nome": p.nome, "descricao": p.descricao} for p in self._plugins.values()
        ]
