"""Plugin de pesquisa: busca resumos na Wikipedia."""

from __future__ import annotations

from backend.core.intent_engine import IntentDefinition
from backend.plugins.base_plugin import BasePlugin, PluginContext
from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import wikipedia

    wikipedia.set_lang("pt")
    _WIKIPEDIA_DISPONIVEL = True
except ImportError:  # pragma: no cover - dependência opcional
    _WIKIPEDIA_DISPONIVEL = False


class PesquisaPlugin(BasePlugin):
    """Pesquisa um termo e retorna um resumo da Wikipédia."""

    nome = "pesquisa"
    descricao = "Pesquisa um assunto e resume o resultado (Wikipedia)."

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="pesquisar",
                frases_exemplo=[
                    "pesquise sobre",
                    "quero pesquisar",
                    "me fale sobre",
                    "o que é",
                    "pesquisar isso",
                    "me explica",
                    "quem foi",
                    "quem é",
                    "me diga o que é",
                    "voce sabe o que e",
                ],
                palavras_chave=[
                    "pesquisar", "pesquise", "buscar sobre", "o que e",
                    "me explica", "quem foi", "quem e", "me fale sobre",
                ],
            )
        ]

    def executar(self, contexto: PluginContext) -> str:
        termo = contexto.entidade or contexto.ultimo_topico

        if not termo:
            return "O que você gostaria que eu pesquisasse?"

        if not _WIKIPEDIA_DISPONIVEL:
            return "O módulo de pesquisa não está instalado no momento."

        try:
            resultado = wikipedia.summary(termo, sentences=3, auto_suggest=False)
            return resultado
        except Exception:
            logger.warning("Falha ao pesquisar termo '%s' na Wikipedia", termo)
            return f"Não encontrei informações confiáveis sobre '{termo}'."
