from moduvent import emit, subscribe

from actions.events import DrawCard, PostPhase, SetPhase
from phase.enum import PHASE
from phase.events import TurnChance


@subscribe(PostPhase, lambda e: e.phase.phase == PHASE.DRAW)
def emit_turn_chance(event: SetPhase):
    emit(TurnChance(duel=event.duel, next_player=event.duel.opponent_player))


@subscribe(TurnChance)
def increase_turn_count(event: TurnChance):
    event.duel.turn_count += 1


@subscribe(PostPhase, lambda e: e.phase.phase == PHASE.DRAW)
def draw_card(event: SetPhase):
    duel, player = event.duel, event.phase.player
    emit(DrawCard(duel=duel, player=player, num=1))
