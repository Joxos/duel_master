"""Kernel execution listeners.

This module holds state-mutating listeners registered on the kernel dispatcher.
These listeners apply concrete execution affairs and report completion back to
the duel dispatcher through the kernel.
"""

from affairon.listen import listen

from duel_core.affairs import (
    AdvanceTurn,
    DrawCard,
    EnterPhase,
    LpVary,
    MultiAffair,
    NormalSummon,
    SendToGraveyard,
)
from duel_core.phase import Phase


@listen(MultiAffair)
def apply_multi_affair(affair: MultiAffair) -> None:
    kernel = affair.duel.kernel
    for child in affair.children:
        kernel.dispatcher.emit(child)
    kernel.complete(affair)


@listen(DrawCard)
def apply_draw_card(affair: DrawCard) -> None:
    drawn_card = affair.player.main_deck.draw(1)[0]
    if drawn_card is not affair.card:
        raise ValueError("DrawCard must apply the planned card")
    affair.player.hand.append(drawn_card)


@listen(EnterPhase, when=lambda affair: affair.phase is Phase.END)
def complete_end_phase(affair: EnterPhase) -> None:
    kernel = affair.duel.kernel
    kernel.state.phase = affair.phase
    kernel.complete(affair)
    kernel.dispatcher.emit(
        AdvanceTurn(
            duel=affair.duel,
            from_turn=kernel.state.current_turn_count,
            to_turn=kernel.state.current_turn_count + 1,
            from_player=kernel.state.current_player,
            to_player=kernel.state.opponent_of(kernel.state.current_player),
            normal_summon_used_from=kernel.state.normal_summon_used,
            normal_summon_used_to=False,
        )
    )


@listen(EnterPhase, when=lambda affair: affair.phase is not Phase.END)
def apply_phase_entry(affair: EnterPhase) -> None:
    kernel = affair.duel.kernel
    kernel.state.phase = affair.phase
    kernel.complete(affair)


@listen(AdvanceTurn)
def apply_advance_turn(affair: AdvanceTurn) -> None:
    kernel = affair.duel.kernel
    kernel.state.current_player = affair.to_player
    kernel.state.current_turn_count = affair.to_turn
    kernel.state.normal_summon_used = affair.normal_summon_used_to
    kernel.complete(affair)
    kernel.do(
        EnterPhase(
            duel=affair.duel,
            phase=Phase.DRAW,
            source_phase=Phase.END,
            requester=apply_advance_turn,
        )
    )


@listen(NormalSummon)
def apply_normal_summon(affair: NormalSummon) -> None:
    kernel = affair.duel.kernel
    affair.player.monster_zones[affair.to_monster_zone_index] = affair.player.hand.pop(
        affair.from_hand_index
    )
    affair.card.representation = affair.to_representation
    kernel.state.normal_summon_used = affair.normal_summon_used_to
    kernel.complete(affair)


@listen(SendToGraveyard)
def apply_send_to_graveyard(affair: SendToGraveyard) -> None:
    affair.player.monster_zones[affair.from_monster_zone_index] = None
    affair.card.representation = affair.to_representation
    affair.player.graveyard.insert(affair.to_graveyard_index, affair.card)


@listen(LpVary)
def apply_lp_vary(affair: LpVary) -> None:
    affair.player.life_points += affair.delta
