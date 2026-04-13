from __future__ import annotations

from affairon import listen

from duel_core.mr2020.battle.affairs import Attack
from duel_core.mr2020.card.affairs import MoveCard
from duel_core.mr2020.card.listeners import apply_move_card
from duel_core.mr2020.duel.affairs import AvailableActions, CompletedAffair, DuelInit, MultiAction
from duel_core.mr2020.forbid.affairs import Forbid
from duel_core.mr2020.forbid.listeners import inject_active_forbids
from duel_core.mr2020.life_point.affairs import LpVary
from duel_core.mr2020.life_point.listeners import apply_lp_vary
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.listeners import offer_phase_actions
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.timing.affairs import AtomicAction
from duel_core.mr2020.card.models import REPRESENTATION


@listen(DuelInit, after=[inject_active_forbids])
def forbid_first_turn_battle(affair: DuelInit) -> None:
    affair.duel.emit(
        Forbid(
            duel=affair.duel,
            target=EnterPhase(
                duel=affair.duel,
                phase=Phase.BATTLE,
                source_phase=Phase.MAIN_1,
                requester=offer_phase_actions,
            ),
            inactive_from_turn=affair.duel.get_current_turn_count() + 1,
        )
    )


@listen(AvailableActions)
def offer_attacks(affair: AvailableActions) -> None:
    if affair.duel.get_phase() is not Phase.BATTLE:
        return

    attacker = affair.duel.get_current_player()
    defender = affair.duel.opponent_of(attacker)
    for attacker_zone in attacker.monster_zones:
        attacker_card = attacker_zone.card
        if attacker_card is None or attacker_card.representation is not REPRESENTATION.ATTACK:
            continue
        if all(zone.card is None for zone in defender.monster_zones):
            affair.actions.append(
                Attack(
                    duel=affair.duel,
                    player=attacker,
                    attacker=attacker_card,
                    requester=offer_attacks,
                )
            )
            continue
        for defender_zone in defender.monster_zones:
            defender_card = defender_zone.card
            if defender_card is None:
                continue
            affair.actions.append(
                Attack(
                    duel=affair.duel,
                    player=attacker,
                    attacker=attacker_card,
                    defender=defender_card,
                    requester=offer_attacks,
                )
            )


@listen(Attack)
def apply_attack(affair: Attack) -> None:
    attacker_atk = affair.attacker.card.atk
    if attacker_atk is None:
        raise ValueError("Attack requires attacker ATK")

    defender_player = affair.duel.opponent_of(affair.player)
    children: list[AtomicAction] = []

    if affair.defender is None:
        children.append(LpVary(duel=affair.duel, player=defender_player, delta=-attacker_atk))
    else:
        defender_atk = affair.defender.card.atk
        if defender_atk is None:
            raise ValueError("Attack requires defender ATK")
        if attacker_atk > defender_atk:
            children.append(
                MoveCard(
                    duel=affair.duel,
                    player=defender_player,
                    card=affair.defender,
                    from_area="monster_zone",
                    to_area="graveyard",
                    from_zone=next(
                        zone
                        for zone in defender_player.monster_zones
                        if zone.card is affair.defender
                    ),
                    from_representation=affair.defender.representation,
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
                    card=affair.attacker,
                    from_area="monster_zone",
                    to_area="graveyard",
                    from_zone=next(
                        zone for zone in affair.player.monster_zones if zone.card is affair.attacker
                    ),
                    from_representation=affair.attacker.representation,
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
                    card=affair.attacker,
                    from_area="monster_zone",
                    to_area="graveyard",
                    from_zone=next(
                        zone for zone in affair.player.monster_zones if zone.card is affair.attacker
                    ),
                    from_representation=affair.attacker.representation,
                    to_representation=REPRESENTATION.VOID,
                )
            )
            children.append(
                MoveCard(
                    duel=affair.duel,
                    player=defender_player,
                    card=affair.defender,
                    from_area="monster_zone",
                    to_area="graveyard",
                    from_zone=next(
                        zone
                        for zone in defender_player.monster_zones
                        if zone.card is affair.defender
                    ),
                    from_representation=affair.defender.representation,
                    to_representation=REPRESENTATION.VOID,
                )
            )

    multi = MultiAction(
        duel=affair.duel,
        requester=affair.requester,
        origin=affair,
        children=children,
    )
    for child in multi.children:
        if isinstance(child, MoveCard):
            apply_move_card(child)
        elif isinstance(child, LpVary):
            apply_lp_vary(child)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=multi))
