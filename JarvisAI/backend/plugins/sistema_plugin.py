"""Plugin que expõe o status do sistema em linguagem natural."""

from __future__ import annotations

from backend.core.intent_engine import IntentDefinition
from backend.plugins.base_plugin import BasePlugin, PluginContext
from backend.services.system_monitor import SystemMonitor


class SistemaPlugin(BasePlugin):
    """Informa o status atual de CPU, RAM e disco em resposta a
    perguntas como 'como está meu computador?'."""

    nome = "sistema"
    descricao = "Relata o status de CPU, RAM e disco do computador."

    def __init__(self, monitor: SystemMonitor | None = None) -> None:
        self._monitor = monitor or SystemMonitor()

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="status_sistema",
                frases_exemplo=[
                    "como esta meu computador",
                    "status do sistema",
                    "verificar sistema",
                    "uso da cpu",
                    "uso da memoria",
                    "como esta a maquina",
                    "quanto de memoria esta usando",
                    "meu pc esta lento",
                    "verifica o desempenho",
                ],
                palavras_chave=[
                    "meu computador", "status do sistema", "uso da cpu",
                    "minha maquina", "meu pc", "desempenho do sistema",
                ],
            )
        ]

    def executar(self, contexto: PluginContext) -> str:
        snap = self._monitor.coletar()

        return (
            f"Sistema: {snap.sistema_operacional}\n"
            f"CPU: {snap.cpu_percent}%\n"
            f"RAM: {snap.ram_percent}% ({snap.ram_usada_gb}GB de {snap.ram_total_gb}GB)\n"
            f"Disco: {snap.disco_percent}% ({snap.disco_usado_gb}GB de {snap.disco_total_gb}GB)"
        )
