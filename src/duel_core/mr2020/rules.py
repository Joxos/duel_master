from affairon.listen import listen

from duel_core.affairs import (
    Attack,
    AvailableActions,
    CompletedAffair,
    Draw,
    DuelInit,
    EnterPhase,
    Forbid,
    completed_enter_phase,
)
from duel_core.models import REPRESENTATION
from duel_core.mr2020.actions import NormalSummon
from duel_core.phase import Phase

TURN_DRAW_NUM = 1
INITIAL_DRAW_NUM = 5
INITIAL_LIFE_POINTS = 8000

PHASE_GRAPH: dict[Phase, tuple[Phase, ...]] = {
    Phase.DRAW: (Phase.STANDBY,),
    Phase.STANDBY: (Phase.MAIN_1,),
    Phase.MAIN_1: (Phase.BATTLE, Phase.END),
    Phase.BATTLE: (Phase.MAIN_2,),
    Phase.MAIN_2: (Phase.END,),
}


@listen(CompletedAffair, when=completed_enter_phase(Phase.DRAW))
def turn_draw(completed: CompletedAffair) -> None:
    affair = completed.affair
    affair.duel.do(
        Draw(
            duel=affair.duel,
            player=affair.duel.state.current_player,
            num=TURN_DRAW_NUM,
            requester=turn_draw,
        )
    )


@listen(DuelInit)
def initial_draw(affair: DuelInit) -> None:
    for player in affair.duel.state.players:
        affair.duel.do(
            Draw(
                duel=affair.duel,
                player=player,
                num=INITIAL_DRAW_NUM,
                requester=initial_draw,
            )
        )


@listen(DuelInit)
def assign_initial_life_points(affair: DuelInit) -> None:
    for player in affair.duel.state.players:
        player.life_points = INITIAL_LIFE_POINTS


@listen(DuelInit)
def forbid_initial_turn_draw(affair: DuelInit) -> None:
    draw_action = Draw(
        duel=affair.duel,
        player=affair.duel.state.current_player,
        num=TURN_DRAW_NUM,
        requester=turn_draw,
    )
    affair.duel.dispatcher.emit(
        Forbid(
            duel=affair.duel,
            target=draw_action,
            inactive_from_turn=affair.duel.state.current_turn_count + 1,
        )
    )


@listen(DuelInit)
def forbid_first_turn_battle(affair: DuelInit) -> None:
    battle_action = EnterPhase(
        duel=affair.duel,
        phase=Phase.BATTLE,
        source_phase=Phase.MAIN_1,
        requester=phase_actions,
    )
    affair.duel.dispatcher.emit(
        Forbid(
            duel=affair.duel,
            target=battle_action,
            inactive_from_turn=affair.duel.state.current_turn_count + 1,
        )
    )


@listen(AvailableActions)
def phase_actions(affair: AvailableActions) -> None:
    for target_phase in PHASE_GRAPH.get(affair.duel.state.phase, ()):
        action = EnterPhase(
            duel=affair.duel,
            phase=target_phase,
            source_phase=affair.duel.state.phase,
            requester=phase_actions,
        )
        if affair.duel.kernel.is_forbidden(action):
            continue
        affair.actions.append(action)


@listen(AvailableActions)
def normal_summon_actions(affair: AvailableActions) -> None:
    if affair.duel.state.phase not in (Phase.MAIN_1, Phase.MAIN_2):
        return
    if affair.duel.state.normal_summon_used:
        return
    empty_zone = next(
        (zone for zone in affair.duel.state.current_player.monster_zones if zone.card is None),
        None,
    )
    if empty_zone is None:
        return
    for card in affair.duel.state.current_player.hand:
        if card.card.level is None or card.card.level > 4:
            continue
        affair.actions.append(
            NormalSummon(
                duel=affair.duel,
                player=affair.duel.state.current_player,
                card=card,
                to_zone=empty_zone,
                from_representation=card.representation,
                to_representation=REPRESENTATION.ATTACK,
                normal_summon_used_from=affair.duel.state.normal_summon_used,
                normal_summon_used_to=True,
                requester=normal_summon_actions,
            )
        )


@listen(AvailableActions)
def battle_actions(affair: AvailableActions) -> None:
    if affair.duel.state.phase is not Phase.BATTLE:
        return
    attacker = affair.duel.state.current_player
    defender = affair.duel.state.opponent_of(attacker)
    for attacker_zone in attacker.monster_zones:
        attacker_card = attacker_zone.card
        if attacker_card is None:
            continue
        if attacker_card.representation is not REPRESENTATION.ATTACK:
            continue
        if all(zone.card is None for zone in defender.monster_zones):
            affair.actions.append(
                Attack(
                    duel=affair.duel,
                    player=attacker,
                    attacker=attacker_card,
                    requester=battle_actions,
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
                    requester=battle_actions,
                )
            )
