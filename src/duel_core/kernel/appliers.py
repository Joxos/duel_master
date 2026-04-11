"""Kernel execution listeners.

This module holds state-mutating listeners registered on the kernel dispatcher.
These listeners apply concrete execution affairs and report completion back to
the duel dispatcher through the kernel.
"""

from affairon.listen import listen

from duel_core.affairs import (
    AdvanceTurn,
    EnterPhase,
    LpVary,
    MoveCard,
    MultiAffair,
    NormalSummon,
)
from duel_core.phase import Phase


@listen(MultiAffair)
def apply_multi_affair(affair: MultiAffair) -> None:
    kernel = affair.duel.kernel
    for child in affair.children:
        kernel.dispatcher.emit(child)
    kernel.complete(affair)


@listen(MoveCard)
def apply_move_card(affair: MoveCard) -> None:
    if affair.from_area == "main_deck":
        if not affair.player.main_deck.cards or affair.player.main_deck.cards[0] is not affair.card:
            raise ValueError("MoveCard must remove the planned top-deck card")
        affair.player.main_deck.cards.pop(0)
    elif affair.from_area == "hand":
        try:
            hand_index = affair.player.hand.index(affair.card)
        except ValueError as exc:
            raise ValueError("MoveCard source card must exist in hand") from exc
        affair.player.hand.pop(hand_index)
    elif affair.from_area == "monster_zone":
        if affair.from_zone is None or affair.from_zone.card is not affair.card:
            raise ValueError("MoveCard source zone must hold the planned card")
        affair.from_zone.card = None
    else:
        raise ValueError(f"Unsupported source area: {affair.from_area}")

    affair.card.representation = affair.to_representation

    if affair.to_area == "hand":
        affair.player.hand.append(affair.card)
        return
    if affair.to_area == "graveyard":
        affair.player.graveyard.append(affair.card)
        return
    if affair.to_area == "monster_zone":
        if affair.to_zone is None:
            raise ValueError("MoveCard target zone is required")
        if affair.to_zone.card is not None:
            raise ValueError("MoveCard target zone must be empty")
        affair.to_zone.card = affair.card
        return

    raise ValueError(f"Unsupported target area: {affair.to_area}")


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
    kernel.dispatcher.emit(
        MoveCard(
            duel=affair.duel,
            player=affair.player,
            card=affair.card,
            from_area="hand",
            to_area="monster_zone",
            to_zone=affair.to_zone,
            from_representation=affair.from_representation,
            to_representation=affair.to_representation,
        )
    )
    kernel.state.normal_summon_used = affair.normal_summon_used_to
    kernel.complete(affair)


@listen(LpVary)
def apply_lp_vary(affair: LpVary) -> None:
    affair.player.life_points += affair.delta
