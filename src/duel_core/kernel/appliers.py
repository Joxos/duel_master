"""Kernel execution listeners.

This module holds state-mutating listeners registered on the kernel dispatcher.
These listeners apply concrete execution affairs and report completion back to
the duel dispatcher through the kernel.
"""

from affairon.listen import listen

from duel_core.affairs import (
    Draw,
    EnterPhase,
    LpVary,
    MultiAffair,
    NormalSummon,
    SendToGraveyard,
    TurnCleanup,
)
from duel_core.models import RuntimeCard, REPRESENTATION
from duel_core.phase import Phase


@listen(MultiAffair)
def on_multi_affair(affair: MultiAffair) -> None:
    kernel = affair.duel.kernel
    for child in affair.children:
        kernel.dispatcher.emit(child)
    kernel.complete(affair)


@listen(Draw)
def on_draw(affair: Draw) -> None:
    kernel = affair.duel.kernel
    drawn = affair.player.main_deck.draw(affair.num)
    affair.player.hand.extend(RuntimeCard(card=c) for c in drawn)
    kernel.complete(affair)


@listen(EnterPhase)
def on_enter_phase(affair: EnterPhase) -> None:
    kernel = affair.duel.kernel
    if affair.phase is Phase.END:
        kernel.state.phase = affair.phase
        kernel.complete(affair)
        kernel.state.current_player = kernel.state.opponent
        kernel.state.current_turn += 1
        kernel.duel_dispatcher.emit(TurnCleanup(duel=affair.duel, turn=kernel.state.current_turn))
        kernel.do(
            EnterPhase(
                duel=affair.duel,
                phase=Phase.DRAW,
                source_phase=affair.phase,
                requester=on_enter_phase,
            )
        )
        return
    kernel.state.phase = affair.phase
    kernel.complete(affair)


@listen(NormalSummon)
def on_normal_summon(affair: NormalSummon) -> None:
    kernel = affair.duel.kernel
    if kernel.state.normal_summon_used:
        raise ValueError("Normal summon already used this turn")
    empty_zone = affair.player.monster_zones.index(None)
    hand_index = affair.player.hand.index(affair.card)
    affair.player.monster_zones[empty_zone] = affair.player.hand.pop(hand_index)
    affair.card.representation = REPRESENTATION.ATTACK
    kernel.state.normal_summon_used = True
    kernel.complete(affair)


@listen(SendToGraveyard)
def on_send_to_graveyard(affair: SendToGraveyard) -> None:
    zone_index = affair.player.monster_zones.index(affair.card)
    affair.player.monster_zones[zone_index] = None
    affair.card.representation = REPRESENTATION.VOID
    affair.player.graveyard.append(affair.card)


@listen(LpVary)
def on_lp_vary(affair: LpVary) -> None:
    affair.player.life_points += affair.delta
