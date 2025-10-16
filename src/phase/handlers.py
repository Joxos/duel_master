from moduvent import emit, subscribe

from actions.events import DrawCard, SetPhase
from phase.enum import PHASE
from phase.events import TurnChance
from phase.models import PhaseWithPlayer
from utils import show_duel_info


@subscribe(SetPhase, lambda e: e.phase.phase == PHASE.TURN_CHANCE)
def emit_turn_chance(event: SetPhase):
    emit(TurnChance(duel=event.duel, next_player=event.duel.opponent_player))


@subscribe(TurnChance)
def increase_turn_count(event: TurnChance):
    event.duel.turn_count += 1
    show_duel_info(event.duel)


@subscribe(TurnChance)
def set_phase(event: TurnChance):
    duel, player = event.duel, event.next_player
    emit(SetPhase(duel=duel, phase=PhaseWithPlayer(PHASE.STANDBY, player)))


@subscribe(SetPhase, lambda e: e.phase.phase == PHASE.DRAW)
def draw_card(event: SetPhase):
    duel, player = event.duel, event.phase.player
    emit(DrawCard(duel=duel, player=player, num=1))
