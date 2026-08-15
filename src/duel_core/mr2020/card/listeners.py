from __future__ import annotations

from affairon import listen

from duel_core.mr2020.card.affairs import MoveCard
from duel_core.mr2020.card.models import Card, REPRESENTATION, RuntimeCard
from duel_core.mr2020.duel.affairs import CompletedAffair, DuelInit
from duel_core.mr2020.player.runtime import PlayerRuntime


@listen(DuelInit)
def normalize_runtime_cards(affair: DuelInit) -> None:
    next_runtime_id = 1

    def to_runtime(card: Card | RuntimeCard) -> RuntimeCard:
        nonlocal next_runtime_id
        source_card = card.card if isinstance(card, RuntimeCard) else card
        source_representation = (
            card.representation if isinstance(card, RuntimeCard) else REPRESENTATION.VOID
        )
        runtime_card = RuntimeCard(
            runtime_id=next_runtime_id,
            card=source_card,
            representation=source_representation,
        )
        next_runtime_id += 1
        return runtime_card

    for player in affair.duel.inject(PlayerRuntime).players:
        player.main_deck.cards = [to_runtime(card) for card in player.main_deck.cards]
        player.extra_deck.cards = [to_runtime(card) for card in player.extra_deck.cards]


def apply_move_card(affair: MoveCard) -> None:
    if affair.from_area == "main_deck":
        if not affair.player.main_deck.cards or affair.player.main_deck.cards[0] is not affair.card:
            raise ValueError("MoveCard must remove the planned top-deck card")
        affair.player.main_deck.cards.pop(0)
    elif affair.from_area == "hand":
        hand_index = affair.player.hand.index(affair.card)
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


@listen(MoveCard)
def apply_move_card_action(affair: MoveCard) -> None:
    apply_move_card(affair)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
