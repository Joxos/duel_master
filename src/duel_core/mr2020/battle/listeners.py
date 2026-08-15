from __future__ import annotations

from affairon import listen

from duel_core.mr2020.battle.affairs import Attack
from duel_core.mr2020.card.affairs import MoveCard
from duel_core.mr2020.duel.affairs import AvailableActions, DuelInit, MultiAction
from duel_core.mr2020.forbid.affairs import Forbid
from duel_core.mr2020.forbid.listeners import setup_forbid_runtime
from duel_core.mr2020.life_point.affairs import LpVary
from duel_core.mr2020.phase.runtime import PhaseRuntime
from duel_core.mr2020.player.runtime import PlayerRuntime
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.listeners import offer_phase_actions
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.timing.affairs import AtomicAction
from duel_core.mr2020.card.models import REPRESENTATION
from duel_core.mr2020.turn.runtime import TurnRuntime


@listen(DuelInit, after=[setup_forbid_runtime])
def forbid_first_turn_battle(affair: DuelInit) -> None:
    turn_runtime = affair.duel.inject(TurnRuntime)
    affair.duel.emit(
        Forbid(
            duel=affair.duel,
            target=EnterPhase(
                duel=affair.duel,
                phase=Phase.BATTLE,
                source_phase=Phase.MAIN_1,
                requester=offer_phase_actions,
            ),
            inactive_from_turn=turn_runtime.current_turn_count + 1,
        )
    )


@listen(AvailableActions)
def offer_attacks(affair: AvailableActions) -> None:
    duel = affair.duel
    if duel.inject(PhaseRuntime).phase is not Phase.BATTLE:
        return

    player_runtime = duel.inject(PlayerRuntime)
    attacker = player_runtime.current_player
    defender = player_runtime.opponent_of(attacker)
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

    defender_player = affair.duel.inject(PlayerRuntime).opponent_of(affair.player)
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
    affair.duel.emit(multi)
