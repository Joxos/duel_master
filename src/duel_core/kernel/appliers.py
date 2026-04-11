from affairon.listen import listen

from duel_core.affairs import AdvanceTurn, EnterPhase, LpVary, MoveCard, MultiAction
from duel_core.phase import Phase


def apply_multi_action(affair: MultiAction) -> None:
    for child in affair.children:
        apply_atomic_action(child)
    affair.duel.kernel.complete(affair)


def apply_atomic_action(affair: object) -> None:
    if isinstance(affair, MoveCard):
        apply_move_card(affair)
        return
    if isinstance(affair, LpVary):
        apply_lp_vary(affair)
        return
    if isinstance(affair, AdvanceTurn):
        apply_advance_turn(affair)
        return
    raise ValueError(f"Unsupported atomic action: {type(affair).__name__}")


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


def apply_lp_vary(affair: LpVary) -> None:
    affair.player.life_points += affair.delta


def apply_advance_turn(affair: AdvanceTurn) -> None:
    affair.duel.kernel.state.current_player = affair.to_player
    affair.duel.kernel.state.current_turn_count = affair.to_turn
    affair.duel.kernel.state.normal_summon_used = affair.normal_summon_used_to
    affair.duel.kernel.complete(affair)
    affair.duel.kernel.do(
        EnterPhase(
            duel=affair.duel,
            phase=Phase.DRAW,
            source_phase=Phase.END,
            requester=apply_advance_turn,
        )
    )


@listen(EnterPhase, when=lambda affair: affair.phase is Phase.END)
def complete_end_phase(affair: EnterPhase) -> None:
    affair.duel.kernel.state.phase = affair.phase
    affair.duel.kernel.complete(affair)
    apply_atomic_action(
        AdvanceTurn(
            duel=affair.duel,
            from_turn=affair.duel.kernel.state.current_turn_count,
            to_turn=affair.duel.kernel.state.current_turn_count + 1,
            from_player=affair.duel.kernel.state.current_player,
            to_player=affair.duel.kernel.state.opponent_of(affair.duel.kernel.state.current_player),
            normal_summon_used_from=affair.duel.kernel.state.normal_summon_used,
            normal_summon_used_to=False,
        )
    )


@listen(EnterPhase, when=lambda affair: affair.phase is not Phase.END)
def apply_phase_entry(affair: EnterPhase) -> None:
    affair.duel.kernel.state.phase = affair.phase
    affair.duel.kernel.complete(affair)
