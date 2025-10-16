from moduvent import emit, subscribe

from actions.events import SetPhase
from phase.enum import PHASE
from phase.events import TurnChance
from utils import show_duel_info


@subscribe(SetPhase, lambda e: e.phase.phase == PHASE.DRAW)
def emit_turn_chance(event: SetPhase):
    emit(TurnChance(duel=event.duel, player=event.duel.phase.player))


@subscribe(TurnChance)
def increase_turn_count(event: TurnChance):
    event.duel.turn_count += 1
    show_duel_info(event.duel)
