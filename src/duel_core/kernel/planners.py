"""Kernel planning listeners.

This module holds planner listeners registered on the kernel dispatcher. These
listeners translate executable affairs into concrete execution units such as
``MultiAction``.
"""

from affairon.listen import listen

from duel_core.affairs import (
    Draw,
    Attack,
    DuelAffair,
    LpVary,
    MoveCard,
    MultiAction,
)
from duel_core.kernel.appliers import apply_multi_action
from duel_core.models import REPRESENTATION, RuntimeCard


@listen(Draw)
def plan_draw(affair: Draw) -> None:
    drawn = [
        card
        for card in affair.player.main_deck.cards[: affair.num]
        if isinstance(card, RuntimeCard)
    ]
    apply_multi_action(
        MultiAction(
            duel=affair.duel,
            requester=affair.requester,
            origin=affair,
            children=[
                MoveCard(
                    duel=affair.duel,
                    player=affair.player,
                    card=card,
                    from_area="main_deck",
                    to_area="hand",
                    from_representation=card.representation,
                    to_representation=card.representation,
                )
                for card in drawn
            ],
        )
    )


@listen(Attack)
def plan_attack(affair: Attack) -> None:
    attacker = affair.attacker
    defender_player = affair.duel.kernel.state.opponent_of(affair.player)
    defender = affair.defender
    children: list[DuelAffair] = []
    attacker_atk = attacker.card.atk
    if attacker_atk is None:
        raise ValueError("Attack requires attacker ATK")

    if defender is None:
        children.append(LpVary(duel=affair.duel, player=defender_player, delta=-attacker_atk))
        apply_multi_action(
            MultiAction(
                duel=affair.duel, requester=affair.requester, origin=affair, children=children
            )
        )
        return

    defender_atk = defender.card.atk
    if defender_atk is None:
        raise ValueError("Attack requires defender ATK")

    if attacker_atk > defender_atk:
        children.append(
            MoveCard(
                duel=affair.duel,
                player=defender_player,
                card=defender,
                from_area="monster_zone",
                to_area="graveyard",
                from_zone=next(
                    zone for zone in defender_player.monster_zones if zone.card is defender
                ),
                from_representation=defender.representation,
                to_representation=REPRESENTATION.VOID,
            )
        )
        children.append(
            LpVary(
                duel=affair.duel,
                player=defender_player,
                delta=-(attacker_atk - defender_atk),
            )
        )
    elif attacker_atk < defender_atk:
        children.append(
            MoveCard(
                duel=affair.duel,
                player=affair.player,
                card=attacker,
                from_area="monster_zone",
                to_area="graveyard",
                from_zone=next(
                    zone for zone in affair.player.monster_zones if zone.card is attacker
                ),
                from_representation=attacker.representation,
                to_representation=REPRESENTATION.VOID,
            )
        )
        children.append(
            LpVary(
                duel=affair.duel,
                player=affair.player,
                delta=-(defender_atk - attacker_atk),
            )
        )
    else:
        children.append(
            MoveCard(
                duel=affair.duel,
                player=affair.player,
                card=attacker,
                from_area="monster_zone",
                to_area="graveyard",
                from_zone=next(
                    zone for zone in affair.player.monster_zones if zone.card is attacker
                ),
                from_representation=attacker.representation,
                to_representation=REPRESENTATION.VOID,
            )
        )
        children.append(
            MoveCard(
                duel=affair.duel,
                player=defender_player,
                card=defender,
                from_area="monster_zone",
                to_area="graveyard",
                from_zone=next(
                    zone for zone in defender_player.monster_zones if zone.card is defender
                ),
                from_representation=defender.representation,
                to_representation=REPRESENTATION.VOID,
            )
        )

    apply_multi_action(
        MultiAction(duel=affair.duel, requester=affair.requester, origin=affair, children=children)
    )
