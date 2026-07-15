"""
Motor de classificação de intenções (NLU leve) do JarvisAI.

Substitui o antigo modelo de comparação exata (``if comando == "..."``)
por um sistema que reconhece variações de linguagem natural através de:

1. Correspondência por sinônimos/expressões-gatilho.
2. Similaridade fuzzy (tolerante a erros de digitação).
3. Extração simples de entidades (o "argumento" da intenção).

O motor é propositalmente independente de bibliotecas pesadas de ML
para manter a inicialização rápida — mas a interface (``IntentEngine``)
permite substituir a implementação por um classificador mais avançado
no futuro sem alterar o restante do sistema (padrão Strategy).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.config.settings import settings
from backend.utils.stemmer import stem_frase
from backend.utils.text_utils import contem_palavra, normalizar, similaridade


@dataclass(frozen=True)
class IntentDefinition:
    """Define uma intenção reconhecível pelo sistema.

    Attributes:
        nome: Identificador único da intenção (ex.: ``"abrir_youtube"``).
        frases_exemplo: Frases de referência usadas na comparação fuzzy.
        palavras_chave: Sinônimos/palavras-gatilho para correspondência
            rápida por presença de substring.
    """

    nome: str
    frases_exemplo: list[str]
    palavras_chave: list[str] = field(default_factory=list)


@dataclass
class IntentResult:
    """Resultado da classificação de uma mensagem do usuário."""

    intent: str
    confianca: float
    entidade: str | None = None
    texto_original: str = ""


class IntentEngine:
    """Classifica mensagens em linguagem natural em intenções conhecidas.

    A lista de intenções é injetada externamente (Dependency Injection),
    de modo que plugins possam registrar suas próprias intenções sem
    acoplar o motor a implementações concretas.
    """

    INTENT_DESCONHECIDA = "desconhecida"

    def __init__(self, intents: list[IntentDefinition] | None = None) -> None:
        self._intents: list[IntentDefinition] = intents or []

    def registrar_intent(self, intent: IntentDefinition) -> None:
        """Adiciona uma nova definição de intenção ao motor (usado pelos
        plugins durante o carregamento)."""

        self._intents.append(intent)

    def classificar(self, texto: str) -> IntentResult:
        """Classifica o texto do usuário na intenção mais provável.

        Estratégia em duas camadas:
            1. Correspondência direta por palavra-chave (rápida, alta
               precisão para comandos comuns).
            2. Similaridade fuzzy contra frases de exemplo (tolerante a
               variações e erros de digitação).

        Args:
            texto: Texto bruto digitado/falado pelo usuário.

        Returns:
            Um :class:`IntentResult` com a intenção mais provável e o
            grau de confiança associado.
        """

        melhor_intent = self.INTENT_DESCONHECIDA
        melhor_confianca = 0.0

        for intent in self._intents:
            if intent.palavras_chave and contem_palavra(texto, intent.palavras_chave):
                # Correspondência por palavra-chave tem prioridade e
                # confiança alta, pois representa um sinônimo direto.
                if 0.9 > melhor_confianca:
                    melhor_intent = intent.nome
                    melhor_confianca = 0.9

            for frase in intent.frases_exemplo:
                score = similaridade(texto, frase)

                # Camada extra: compara também as versões "radicalizadas"
                # (stemming leve), o que ajuda a reconhecer variações
                # verbais que a similaridade literal não captura bem
                # (ex.: "pesquisando" vs. "pesquisar").
                score_stem = similaridade(stem_frase(normalizar(texto)), stem_frase(normalizar(frase)))
                score = max(score, score_stem)

                if score > melhor_confianca:
                    melhor_intent = intent.nome
                    melhor_confianca = score

        if melhor_confianca < settings.assistant.intent_confidence_threshold:
            return IntentResult(
                intent=self.INTENT_DESCONHECIDA,
                confianca=melhor_confianca,
                texto_original=texto,
            )

        return IntentResult(
            intent=melhor_intent,
            confianca=melhor_confianca,
            entidade=self._extrair_entidade(texto),
            texto_original=texto,
        )

    @staticmethod
    def _extrair_entidade(texto: str) -> str | None:
        """Extrai a porção "argumento" de um comando, removendo verbos
        de comando comuns.

        Exemplo: "pesquise sobre buracos negros" -> "buracos negros".
        """

        verbos_comando = [
            "pesquisar",
            "pesquise",
            "buscar",
            "busque",
            "tocar",
            "toque",
            "abrir",
            "abra",
            "quero",
            "sobre",
            "me",
            "lembre",
            "lembrete",
            "anote",
            "anotar",
            "adicionar",
            "tarefa",
            "criar",
            "de",
            "que",
            "preciso",
        ]

        texto_norm = normalizar(texto)
        tokens = [t for t in texto_norm.split() if t not in verbos_comando]

        entidade = " ".join(tokens).strip()
        return entidade or None
