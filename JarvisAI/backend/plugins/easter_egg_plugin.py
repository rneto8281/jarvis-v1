"""
Plugin de easter egg: frases especiais com comportamento personalizado.

Mantido separado dos demais plugins de comando porque representa uma
regra de negócio "pessoal" do usuário (uma frase-gatilho específica),
e não uma categoria genérica de funcionalidade — assim fica fácil
adicionar ou remover frases assim no futuro sem mexer em outros
plugins.
"""

from __future__ import annotations

import webbrowser

from backend.core.intent_engine import IntentDefinition
from backend.plugins.base_plugin import BasePlugin, PluginContext
from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pywhatkit

    _PYWHATKIT_DISPONIVEL = True
except ImportError:  # pragma: no cover - dependência opcional
    _PYWHATKIT_DISPONIVEL = False


class EasterEggPlugin(BasePlugin):
    """Trata a frase de ativação especial do usuário."""

    nome = "easter_egg"
    descricao = "Frase de ativação pessoal: abre uma música específica no YouTube."

    _MUSICA_ALVO = "Back In Black Iron Man"

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="papai_chegou",
                frases_exemplo=[
                    "acorda que o papai chegou",
                    "acordou que o papai chegou",
                ],
                # Frase bem específica: usar como palavra-chave garante alta
                # confiança e evita colisão com o plugin de música genérico.
                palavras_chave=["acorda que o papai chegou", "papai chegou"],
            )
        ]

    def executar(self, contexto: PluginContext) -> str:
        if _PYWHATKIT_DISPONIVEL:
            try:
                pywhatkit.playonyt(self._MUSICA_ALVO)
                return "Bem-vindo de volta, chefe. Tocando sua música."
            except Exception:
                logger.warning("Falha ao tocar '%s' via pywhatkit", self._MUSICA_ALVO)

        # Fallback: abre a busca do YouTube diretamente no navegador.
        termo_busca = self._MUSICA_ALVO.replace(" ", "+")
        webbrowser.open(f"https://www.youtube.com/results?search_query={termo_busca}")
        return "Bem-vindo de volta, chefe. Abrindo sua música no YouTube."
