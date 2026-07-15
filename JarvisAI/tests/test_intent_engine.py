"""Testes unitários do motor de classificação de intenções."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.intent_engine import IntentDefinition, IntentEngine


def _motor_exemplo() -> IntentEngine:
    motor = IntentEngine()
    motor.registrar_intent(
        IntentDefinition(
            nome="abrir_youtube",
            frases_exemplo=["abra o youtube", "abrir youtube"],
            palavras_chave=["abrir youtube", "abra o youtube"],
        )
    )
    motor.registrar_intent(
        IntentDefinition(
            nome="pesquisar",
            frases_exemplo=["pesquise sobre", "quero pesquisar"],
            palavras_chave=["pesquisar", "pesquise"],
        )
    )
    return motor


def test_reconhece_variacoes_da_mesma_intencao():
    motor = _motor_exemplo()

    assert motor.classificar("abra o youtube").intent == "abrir_youtube"
    assert motor.classificar("abrir youtube por favor").intent == "abrir_youtube"


def test_frase_desconhecida_retorna_intent_desconhecida():
    motor = _motor_exemplo()

    resultado = motor.classificar("xablau tarugo perinola")
    assert resultado.intent == IntentEngine.INTENT_DESCONHECIDA


def test_extracao_de_entidade_remove_verbo_de_comando():
    motor = _motor_exemplo()

    resultado = motor.classificar("pesquise sobre buracos negros")
    assert "buracos negros" in resultado.entidade
