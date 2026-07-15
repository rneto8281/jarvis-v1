"""Testes unitários do gerenciador de contexto de conversa."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.context_manager import ContextManager


def test_registra_e_recupera_ultimo_topico():
    ctx = ContextManager(max_turnos=5)
    ctx.registrar_turno("pesquise sobre marte", "pesquisar", "resposta", "marte")

    assert ctx.ultimo_topico == "marte"
    assert ctx.ultimo_intent() == "pesquisar"


def test_janela_deslizante_descarta_turnos_antigos():
    ctx = ContextManager(max_turnos=2)

    ctx.registrar_turno("msg1", "intent1", "r1", None)
    ctx.registrar_turno("msg2", "intent2", "r2", None)
    ctx.registrar_turno("msg3", "intent3", "r3", None)

    assert len(ctx.historico) == 2
    assert ctx.historico[0].mensagem_usuario == "msg2"
