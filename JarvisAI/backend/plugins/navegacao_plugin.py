"""Plugin de navegação: abre sites comuns (Google, YouTube)."""

from __future__ import annotations

import webbrowser

from backend.core.intent_engine import IntentDefinition
from backend.plugins.base_plugin import BasePlugin, PluginContext


class NavegacaoPlugin(BasePlugin):
    """Abre páginas web comuns a partir de comandos de voz/texto."""

    nome = "navegacao"
    descricao = "Abre sites como Google e YouTube no navegador padrão."

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="abrir_google",
                frases_exemplo=[
                    "abra o google", "abrir google", "abre o navegador",
                    "quero pesquisar no google", "acesse o google", "entra no google",
                ],
                palavras_chave=["abrir google", "abra o google", "abre o google", "acessar google"],
            ),
            IntentDefinition(
                nome="abrir_youtube",
                frases_exemplo=[
                    "abra o youtube", "abrir youtube", "quero ver videos",
                    "acesse o youtube", "entra no youtube", "abre o youtube",
                ],
                palavras_chave=["abrir youtube", "abra o youtube", "abre o youtube", "acessar youtube"],
            ),
        ]

    def executar(self, contexto: PluginContext) -> str:
        texto = contexto.texto_original.lower()

        if "youtube" in texto:
            webbrowser.open("https://www.youtube.com")
            return "Abrindo o YouTube."

        webbrowser.open("https://www.google.com")
        return "Abrindo o Google."
