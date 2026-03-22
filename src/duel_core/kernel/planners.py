"""Kernel planning listeners.

This module holds planner listeners registered on the kernel dispatcher. These
listeners translate executable affairs into concrete execution units such as
``MultiAffair``.
"""

from affairon.listen import listen

from duel_core.affairs import Attack, DuelAffair, LpVary, MultiAffair, SendToGraveyard


@listen(Attack)
def on_attack(affair: Attack) -> None:
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
            MultiAffair(duel=affair.duel, requester=on_attack, children=children)
        )
        return

    defender_atk = defender.card.atk
    if defender_atk is None:
        raise ValueError("Attack requires defender ATK")

    if attacker_atk > defender_atk:
        children.append(SendToGraveyard(duel=affair.duel, player=defender_player, card=defender))
        children.append(
            LpVary(
                duel=affair.duel,
                player=defender_player,
                delta=-(attacker_atk - defender_atk),
            )
        )
    elif attacker_atk < defender_atk:
        children.append(SendToGraveyard(duel=affair.duel, player=affair.player, card=attacker))
        children.append(
            LpVary(
                duel=affair.duel,
                player=affair.player,
                delta=-(defender_atk - attacker_atk),
            )
        )
    else:
        children.append(SendToGraveyard(duel=affair.duel, player=affair.player, card=attacker))
        children.append(SendToGraveyard(duel=affair.duel, player=defender_player, card=defender))

    kernel.dispatcher.emit(MultiAffair(duel=affair.duel, requester=on_attack, children=children))
