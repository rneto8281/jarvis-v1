"""
Motor central do JarvisAI (fachada/orquestrador principal).

Este módulo implementa o padrão Facade: expõe uma interface única e
simples (``processar_mensagem``) para a API, escondendo a complexidade
da colaboração entre o motor de intenções, o gerenciador de contexto,
o gerenciador de plugins e a memória de longo prazo.

É este componente que a interface web (via API) e uma futura interface
de voz consumem — ambas usam exatamente o mesmo "cérebro".
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.core.context_manager import ContextManager
from backend.core.event_bus import event_bus
from backend.core.intent_engine import IntentEngine
from backend.core.plugin_manager import PluginManager
from backend.core.response_builder import ResponseBuilder
from backend.memory.memory_manager import MemoryManager
from backend.plugins.base_plugin import PluginContext
from backend.security.sanitizer import EntradaInvalida, sanitizar_texto
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RespostaJarvis:
    """Resultado completo do processamento de uma mensagem do usuário."""

    resposta: str
    intent: str
    confianca: float


class JarvisEngine:
    """Orquestra o pipeline completo de processamento de uma mensagem:

    1. Classifica a intenção (``IntentEngine``).
    2. Resolve o contexto (ex.: referências ao último assunto).
    3. Despacha para o plugin responsável (``PluginManager``).
    4. Registra o turno no contexto e na memória de longo prazo.
    5. Publica eventos para quem estiver ouvindo (ex.: animações da UI).
    """

    def __init__(
        self,
        intent_engine: IntentEngine,
        plugin_manager: PluginManager,
        context_manager: ContextManager,
        memory_manager: MemoryManager,
        response_builder: ResponseBuilder | None = None,
    ) -> None:
        self._intent_engine = intent_engine
        self._plugin_manager = plugin_manager
        self._context = context_manager
        self._memory = memory_manager
        self._responses = response_builder or ResponseBuilder()

    @property
    def memory(self) -> MemoryManager:
        """Expõe o gerenciador de memória para consumidores externos
        (ex.: endpoints da API que precisam consultar perfil/tarefas)."""

        return self._memory

    @property
    def plugin_manager(self) -> PluginManager:
        """Expõe o gerenciador de plugins (ex.: endpoint de listagem)."""

        return self._plugin_manager

    def processar_mensagem(self, texto_usuario: str) -> RespostaJarvis:
        """Processa uma mensagem do usuário do início ao fim.

        Args:
            texto_usuario: Texto bruto enviado pelo usuário (chat ou voz).

        Returns:
            Um :class:`RespostaJarvis` com a resposta final e metadados
            de classificação, prontos para serem enviados à interface.
        """

        event_bus.publicar("mensagem_recebida", texto=texto_usuario)

        try:
            texto_usuario = sanitizar_texto(texto_usuario)
        except EntradaInvalida as erro:
            resposta_invalida = RespostaJarvis(
                resposta=f"Não posso processar essa mensagem: {erro}",
                intent="entrada_invalida",
                confianca=0.0,
            )
            event_bus.publicar(
                "resposta_gerada", texto=resposta_invalida.resposta, intent=resposta_invalida.intent
            )
            return resposta_invalida

        resultado = self._intent_engine.classificar(texto_usuario)

        if resultado.intent == self._intent_engine.INTENT_DESCONHECIDA:
            resposta_texto = self._responses.nao_compreendido(texto_usuario)
        else:
            contexto = PluginContext(
                texto_original=texto_usuario,
                entidade=resultado.entidade,
                ultimo_topico=self._context.ultimo_topico,
                usuario=self._memory.obter_perfil().nome,
            )
            resposta_plugin = self._plugin_manager.despachar(resultado.intent, contexto)
            resposta_texto = resposta_plugin or self._responses.nao_compreendido(texto_usuario)

        self._context.registrar_turno(
            mensagem_usuario=texto_usuario,
            intent=resultado.intent,
            resposta=resposta_texto,
            entidade=resultado.entidade,
        )
        self._memory.registrar_conversa(texto_usuario, resultado.intent, resposta_texto)

        event_bus.publicar(
            "resposta_gerada", texto=resposta_texto, intent=resultado.intent
        )

        logger.info(
            "intent=%s confianca=%.2f entrada=%r",
            resultado.intent,
            resultado.confianca,
            texto_usuario,
        )

        return RespostaJarvis(
            resposta=resposta_texto,
            intent=resultado.intent,
            confianca=resultado.confianca,
        )

    def disparar_intent(self, nome_intent: str, texto_referencia: str = "") -> RespostaJarvis:
        """Despacha diretamente uma intenção conhecida, sem passar pelo
        classificador de NLU.

        Usado por gatilhos não-textuais (ex.: detecção de duas palmas),
        onde a intenção já é conhecida de antemão e não há texto real
        do usuário para classificar.

        Args:
            nome_intent: Nome exato da intenção já registrada por algum plugin.
            texto_referencia: Texto opcional só para fins de log/histórico.

        Returns:
            O mesmo formato de resultado usado pelo pipeline normal.
        """

        contexto = PluginContext(
            texto_original=texto_referencia or nome_intent,
            entidade=None,
            ultimo_topico=self._context.ultimo_topico,
            usuario=self._memory.obter_perfil().nome,
        )

        resposta_plugin = self._plugin_manager.despachar(nome_intent, contexto)
        resposta_texto = resposta_plugin or self._responses.nao_compreendido(nome_intent)

        self._context.registrar_turno(
            mensagem_usuario=texto_referencia or f"[gatilho: {nome_intent}]",
            intent=nome_intent,
            resposta=resposta_texto,
            entidade=None,
        )
        self._memory.registrar_conversa(texto_referencia or nome_intent, nome_intent, resposta_texto)

        event_bus.publicar("resposta_gerada", texto=resposta_texto, intent=nome_intent)

        return RespostaJarvis(resposta=resposta_texto, intent=nome_intent, confianca=1.0)
