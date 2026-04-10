"""Kernel planning listeners.

This module holds planner listeners registered on the kernel dispatcher. These
listeners translate executable affairs into concrete execution units such as
``MultiAffair``.
"""

from affairon.listen import listen

from duel_core.affairs import (
    Draw,
    Attack,
    DrawCard,
    DuelAffair,
    LpVary,
    MultiAffair,
    SendToGraveyard,
)
from duel_core.models import REPRESENTATION, RuntimeCard


@listen(Draw)
def plan_draw(affair: Draw) -> None:
    kernel = affair.duel.kernel
    drawn = [
        card
        for card in affair.player.main_deck.cards[: affair.num]
        if isinstance(card, RuntimeCard)
    ]
    kernel.dispatcher.emit(
        MultiAffair(
            duel=affair.duel,
            requester=affair.requester,
            origin=affair,
            children=[
                DrawCard(
                    duel=affair.duel,
                    player=affair.player,
                    card=card,
                )
                for card in drawn
            ],
        )
    )


@listen(Attack)
def plan_attack(affair: Attack) -> None:
    kernel = affair.duel.kernel

    attacker = affair.attacker
    defender_player = kernel.state.opponent_of(affair.player)
    defender = affair.defender
    children: list[DuelAffair] = []
    attacker_atk = attacker.card.atk
    if attacker_atk is None:
        raise ValueError("Attack requires attacker ATK")

    if defender is None:
        children.append(LpVary(duel=affair.duel, player=defender_player, delta=-attacker_atk))
        kernel.dispatcher.emit(
            MultiAffair(
                duel=affair.duel, requester=affair.requester, origin=affair, children=children
            )
        )
        return

    defender_atk = defender.card.atk
    if defender_atk is None:
        raise ValueError("Attack requires defender ATK")

    if attacker_atk > defender_atk:
        children.append(
            SendToGraveyard(
                duel=affair.duel,
                player=defender_player,
                card=defender,
                from_monster_zone_index=defender_player.monster_zones.index(defender),
                to_graveyard_index=len(defender_player.graveyard),
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
            SendToGraveyard(
                duel=affair.duel,
                player=affair.player,
                card=attacker,
                from_monster_zone_index=affair.player.monster_zones.index(attacker),
                to_graveyard_index=len(affair.player.graveyard),
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
            SendToGraveyard(
                duel=affair.duel,
                player=affair.player,
                card=attacker,
                from_monster_zone_index=affair.player.monster_zones.index(attacker),
                to_graveyard_index=len(affair.player.graveyard),
                from_representation=attacker.representation,
                to_representation=REPRESENTATION.VOID,
            )
        )
        children.append(
            SendToGraveyard(
                duel=affair.duel,
                player=defender_player,
                card=defender,
                from_monster_zone_index=defender_player.monster_zones.index(defender),
                to_graveyard_index=len(defender_player.graveyard),
                from_representation=defender.representation,
                to_representation=REPRESENTATION.VOID,
            )
        )

    kernel.dispatcher.emit(
        MultiAffair(duel=affair.duel, requester=affair.requester, origin=affair, children=children)
    )
